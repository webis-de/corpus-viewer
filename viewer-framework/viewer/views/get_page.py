from .shared_code import set_sessions, load_data, get_or_create_tag, \
    get_items_by_indices, get_item_by_ids, glob_manager_data, get_current_corpus
import collections
import re
import os
import time
import json
from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect
from django.template import Engine, Context
from django.template.loader import get_template
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from viewer.models import m_Tag, m_Entity
import hashlib

regex_filter_numbers_negative = re.compile('(?<![>|\.|>=|<=|<|<|0|1|2|3|4|5|6|7|8|9|0])(-[0-9]+\.?[0-9]*)')
regex_filter_numbers_positive = re.compile('(?<![>|\.|>=|<=|<|<|0|1|2|3|4|5|6|7|8|9|0|-])([0-9]+\.?[0-9]*)')
regex_filter_numbers_lt = re.compile('<(-?[0-9]+\.?[0-9]*)')
regex_filter_numbers_lte = re.compile('<=(-?[0-9]+\.?[0-9]*)')
regex_filter_numbers_gt = re.compile('>(-?[0-9]+\.?[0-9]*)')
regex_filter_numbers_gte = re.compile('>=(-?[0-9]+\.?[0-9]*)')

def get_page(request):
##### handle session entries
    start_total = time.perf_counter()
    try:
        set_sessions(request)
    except:
        raise Http404("Corpus does not exist")

    id_corpus = get_current_corpus(request)

##### load data and apply filters
    list_ids, info_filter_values = get_filtered_data(request)
    # return JsonResponse({})
    list_tags = []
    # list_tags = get_tags_filtered_items(data_only_ids, request)
##### handle post requests
    if request.method == 'POST':
        response = {}
        obj = json.loads(request.body.decode("utf-8"))
        if obj['task'] == 'add_tag':
            response['data'] = add_tag(obj, data, request)
        elif obj['task'] == 'export_data':
            response = export_data(obj, data, request)
        elif obj['task'] == 'reload_settings':
            glob_manager_data.reload_settings(id_corpus)
        elif obj['task'] == 'reindex_corpus':
            try:
                glob_manager_data.reindex_corpus(obj['id_corpus'])
            except:
                glob_manager_data.reindex_corpus(id_corpus)
        elif obj['task'] == 'get_number_of_indexed_items':
            response['number_of_indexed_items'] = glob_manager_data.get_number_of_indexed_items(obj['id_corpus'])
            response['state_loaded'] = glob_manager_data.get_state_loaded(obj['id_corpus'])
        elif obj['task'] == 'delete_corpus':
            glob_manager_data.delete_corpus(id_corpus)

        return JsonResponse(response)
##### page the dataset
    # paginator = Paginator(range(0, get_setting('page_size', request=request))
    paginator = Paginator(list_ids, glob_manager_data.get_setting_for_corpus('page_size', id_corpus))
    # paginator = Paginator(data, get_setting('page_size', request=request))
    try:
        page_current = paginator.page(request.session[id_corpus]['viewer__viewer__page'])
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        page_current = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        page_current = paginator.page(paginator.num_pages)
##### add tags to the dataset

    start_loading = time.perf_counter()
    data = glob_manager_data.get_items(id_corpus, id_corpus, page_current)
    print('loading time: '+str(round(float(time.perf_counter() - start_loading) * 1000, 2))+'ms')

    # add_tags(data, request)
##### handle post requests
    context = {}
    context['settings'] = glob_manager_data.get_settings_for_corpus(id_corpus)
    # context['page_current'] = page_current
    context['data'] = data

    previous_page_number = None
    next_page_number = None
    if page_current.has_previous():
        previous_page_number = page_current.previous_page_number()
    if page_current.has_next():
        next_page_number = page_current.next_page_number()
    template = get_template('viewer/table.html')

    print('TIME: '+str(round(float(time.perf_counter() - start_total) * 1000, 2))+'ms')

    return JsonResponse({'content': template.render(context, request),
            'tags_filtered_items': list_tags,
            'count_pages': page_current.paginator.num_pages,
            'count_entries': page_current.paginator.count,
            'previous_page_number': previous_page_number,
            'next_page_number': next_page_number,
            'info_filter_values': info_filter_values
        })

def export_data(obj, data, request):
    response = {}

    data_export = []

    if get_setting('data_type', request=request) == 'database':
        raise NotImplementedError("export for database")
    else:
        db_obj_entities = m_Entity.objects.filter(key_corpus=get_current_corpus(request)).prefetch_related('viewer_tags')
        dict_entities = {entity.id_item: entity for entity in db_obj_entities}

        key_tag = obj['key_tag']

        for item in data:
            try:
                item[key_tag] = [{'id': tag.id, 'name': tag.name, 'color': tag.color} for tag in dict_entities[str(item[get_setting('id', request=request)])].viewer_tags.all()]
            except KeyError:
                # if there is no entity entry in the database
                item[key_tag] = []

        data_export = data

    with open('exported_data.ldjson', 'w') as f:
        for line in data_export:
            f.write(json.dumps(line)+'\n')

    return response

def get_filtered_data(request):
    info_filter_values = {}
    id_corpus = get_current_corpus(request)

    dict_filters = get_filters_if_not_empty(request, id_corpus)
    if dict_filters == None:
            return glob_manager_data.get_all_ids_for_corpus(id_corpus, glob_manager_data.get_settings_for_corpus(id_corpus)), info_filter_values
    else:
        bytes_dict_filters = json.dumps(dict_filters, sort_keys=True).encode()
        hash_custom = hashlib.sha1(bytes_dict_filters).hexdigest()
        # fails if the user has no hash stored
        try:
            # checks if the hash corresponds to the last hash
            if hash_custom == request.session[id_corpus]['viewer__last_hash']:
                return request.session[id_corpus]['viewer__last_result']
        except:
            pass
    # print(hash_customs)
    #
    # FILTER BY TAGS 
    #
    # values_filter_tags = request.session[get_current_corpus(request)]['viewer__viewer__filter_tags']
    # if len(values_filter_tags) > 0:
    #     if get_setting('data_type', request=request) == 'database':
    #         # iterate over tag and return only items tagged with them
    #         for tag in values_filter_tags:
    #             data = data.filter(viewer_tags__name=tag)
    #     else:
    #         # filter the data by tags
    #         data = filter_data_tags(data, values_filter_tags, request)

    #
    # FILTERS
    #

    list_data = None
    for obj_filter in glob_manager_data.get_setting_for_corpus('filters', id_corpus):
        # filter the data by the current filter
        list_data_new, info_values, skipped = filter_data(request, obj_filter)
        # print(list_data_new)
        if not skipped:
            if list_data == None:
                list_data = sorted(list_data_new)
            else:
                set_tmp = frozenset(list_data_new)
                list_data = [x for x in list_data if x in set_tmp]
                # list_data = list_data.intersection(list_data_new)
                
            info_filter_values[obj_filter['data_field']] = info_values
    # print(len(data))
    # print(len(list_data))
    if list_data != None:
        # data = [item for item in data if item[get_setting('id', request=request)] in list_data]
        # print(list_data)
        request.session[id_corpus]['viewer__last_hash'] = hash_custom
        request.session[id_corpus]['viewer__last_result'] = list_data, info_filter_values
        return list_data, info_filter_values


    raise Exception("shouldn't reach this!")
    # if no filter was applied return all ids
    #
    # UPDATE data_only_ids
    #
    # if get_setting('data_type', request=request) == 'database':
    #     data_only_ids = [item.id for item in data]
    # else:
    #     # update data_only_ids
    #     data_only_ids = [str(item[get_setting('id', request=request)]) for item in data]

    # return data, data_only_ids, info_filter_values

def filter_data(request, obj_filter):
    list_data = None
    # list_data_new = []
    # set_data_new = set()

    info_values = {}
    id_corpus = get_current_corpus(request)

    skipped = True
    field_id = glob_manager_data.get_setting_for_corpus('id', id_corpus)

    # get the values of the current filter
    values = request.session[id_corpus]['viewer__viewer__filter_custom'][obj_filter['data_field']]

    # if the value is not empty 
    if len(values) != 0:
        skipped = False
        info_values = {value:{'value_count_per_document': 0, 'value_count_total': 0} for value in values}
        if glob_manager_data.get_setting_for_corpus('data_type', id_corpus) == 'database':
            raise ValueError('NOT IMPLEMENTED')
        #     # TODO: make flexible filters for database
        #     data = data.filter(**{obj_filter['data_field']+'__icontains': value})
        else:
            type_data_field = glob_manager_data.get_setting_for_corpus('data_fields', id_corpus)[obj_filter['data_field']]['type']
            # if the filter is 'contains'
            if type_data_field == 'string' or type_data_field == 'text':
                # get the type (string, list) of the data-field
                if type_data_field == 'string':
                    for value in values:
                        is_case_insensitive = True if value[0] == 'i' else False
                        real_value = value[2:]
                        list_data_new = glob_manager_data.get_handle_index(id_corpus).get_string(obj_filter['data_field'], real_value, is_case_insensitive)
                        
                        if list_data == None:
                            list_data = sorted(list_data_new)
                        else:
                            set_tmp = frozenset(list_data_new)
                            list_data = [x for x in list_data if x in set_tmp]
                elif type_data_field == 'text':
                    for value in values:
                        is_case_insensitive = True if value[0] == 'i' else False
                        real_value = value[2:]

                        start = time.perf_counter()
                        list_data_new = glob_manager_data.get_handle_index(id_corpus).get_text(obj_filter['data_field'], real_value, is_case_insensitive)
                        
                        if list_data == None:
                            list_data = sorted(list_data_new)
                        else:
                            set_tmp = frozenset(list_data_new)
                            list_data = [x for x in list_data if x in set_tmp]

                        print('searching time: '+str(round(float(time.perf_counter()-start) * 1000, 2))+'ms')
                
                        # info_values[value]['value_count_total'] = text_lower.count(real_value)
                        # info_values[value]['value_count_per_document'] = 1 
                        # print(list_ids)
        #             for item in data:
        #                 text = str(item[obj_filter['data_field']])
        #                 text_lower = text.lower()
        #                 keep = True

        #                 for value in values:
        #                     is_case_insensitive = True if value[0] == 'i' else False
        #                     real_value = value[2:]

        #                     if is_case_insensitive:
        #                         real_value = real_value.lower()
        #                         if real_value in text_lower:
        #                             info_values[value]['value_count_total'] += text_lower.count(real_value)
        #                             info_values[value]['value_count_per_document'] += 1
        #                         else:
        #                             keep = False
        #                     else:
        #                         if real_value in text:
        #                             info_values[value]['value_count_total'] += text.count(real_value)
        #                             info_values[value]['value_count_per_document'] += 1
        #                         else:
        #                             keep = False

        #                 if keep:
        #                     set_data_new.add(item[field_id])

        #             # data = set_data_new
                        
                elif type_data_field == 'list':
                    raise ValueError('NOT IMPLEMENTED')
        #     # if the filter is 'number'
            elif type_data_field == 'number':
                for value in values:
                    try:
                        value = int(value)
                    except ValueError:
                        value = float(value)

                    list_data_new = glob_manager_data.get_handle_index(id_corpus).get_number(obj_filter['data_field'], int(value))
                       
                    if list_data == None:
                        list_data = sorted(list_data_new)
                    else:
                        set_tmp = frozenset(list_data_new)
                        list_data = [x for x in list_data if x in set_tmp]
        #         values_parsed = parse_values(values)

        #         for item in data:
        #             keep = True
        #             for key, numbers in values_parsed.items():
        #                 if key == 'equal':
        #                     for obj in numbers:
        #                         if item[obj_filter['data_field']] == obj[1]:
        #                             info_values[obj[0]]['value_count_total'] += 1
        #                             info_values[obj[0]]['value_count_per_document'] += 1
        #                         else:
        #                             keep = False
        #                 elif key == 'lt':
        #                     for obj in numbers:
        #                         if item[obj_filter['data_field']] < obj[1]:
        #                             info_values[obj[0]]['value_count_total'] += 1
        #                             info_values[obj[0]]['value_count_per_document'] += 1
        #                         else:
        #                             keep = False
        #                 elif key == 'lte':
        #                     for obj in numbers:
        #                         if item[obj_filter['data_field']] <= obj[1]:
        #                             info_values[obj[0]]['value_count_total'] += 1
        #                             info_values[obj[0]]['value_count_per_document'] += 1
        #                         else:
        #                             keep = False
        #                 elif key == 'gt':
        #                     for obj in numbers:
        #                         if item[obj_filter['data_field']] > obj[1]:
        #                             info_values[obj[0]]['value_count_total'] += 1
        #                             info_values[obj[0]]['value_count_per_document'] += 1
        #                         else:
        #                             keep = False
        #                 elif key == 'gte':
        #                     for obj in numbers:
        #                         if item[obj_filter['data_field']] >= obj[1]:
        #                             info_values[obj[0]]['value_count_total'] += 1
        #                             info_values[obj[0]]['value_count_per_document'] += 1
        #                         else:
        #                             keep = False

        #             if keep:
        #                     set_data_new.add(item[field_id])
                
        #         # data = set_data_new

                # check if a specific number is requested

    if list_data == None:
        list_data = []
    return list_data, info_values, skipped

def get_filters_if_not_empty(request, id_corpus):
    dict_filters = request.session[id_corpus]['viewer__viewer__filter_custom']

    is_empty = True
    for values in dict_filters.values():
        if len(values) != 0:
            is_empty = False
            break

    if is_empty == True:
        return None 
    else:
        return dict_filters

def parse_values(values):
    values_parsed = {}

    for value in values:
        result_positive = regex_filter_numbers_positive.search(value)
        result_negative = regex_filter_numbers_negative.search(value)
        if result_positive != None:
            number = float(result_positive.group(1))
            if not 'equal' in values_parsed:
                values_parsed['equal'] = []
            values_parsed['equal'].append((value, number))
        elif result_negative != None:
            number = float(result_negative.group(1))
            if not 'equal' in values_parsed:
                values_parsed['equal'] = []
            values_parsed['equal'].append((value, number))
        else:
            result_lt = regex_filter_numbers_lt.search(value)
            if result_lt != None:
                number = float(result_lt.group(1))
                if not 'lt' in values_parsed:
                    values_parsed['lt'] = []
                values_parsed['lt'].append((value, number))

            result_lte = regex_filter_numbers_lte.search(value)
            if result_lte != None:
                number = float(result_lte.group(1))
                if not 'lte' in values_parsed:
                    values_parsed['lte'] = []
                values_parsed['lte'].append((value, number))

            result_gt = regex_filter_numbers_gt.search(value)
            if result_gt != None:
                number = float(result_gt.group(1))
                if not 'gt' in values_parsed:
                    values_parsed['gt'] = []
                values_parsed['gt'].append((value, number))
            
            result_gte = regex_filter_numbers_gte.search(value)
            if result_gte != None:
                number = float(result_gte.group(1))
                if not 'gte' in values_parsed:
                    values_parsed['gte'] = []
                values_parsed['gte'].append((value, number))
    return values_parsed

# def filter_data(request, data, obj_filter):
#     info_values = {}
#     # get the value of the current filter
#     values = request.session[get_current_corpus(request)]['viewer__viewer__filter_custom'][obj_filter['data_field']]
#     # if the value is not empty 
#     for value in values:
#         if get_setting('data_type', request=request) == 'database':
#             # TODO: make flexible filters for database
#             data = data.filter(**{obj_filter['data_field']+'__icontains': value})
#         else:
#             # if the filter is 'contains'
#             if obj_filter['type'] == 'contains':
#                 # get the type (string, list) of the data-field
#                 type_data_field = get_setting('data_fields', request=request)[obj_filter['data_field']]['type']
#                 if type_data_field == 'string' or type_data_field == 'text':
#                     # return only items which contain all the values
#                     is_case_insensitive = True if value[0] == 'i' else False
#                     real_value = value[2:]

#                     value_count_per_document = 0
#                     value_count_total = 0
#                     data_new = []

#                     for item in data:
#                         if is_case_insensitive:
#                             real_value = real_value.lower()
#                             text = str(item[obj_filter['data_field']]).lower()
#                         else:
#                             real_value = real_value
#                             text = str(item[obj_filter['data_field']])

#                         if real_value in text:
#                             data_new.append(item)

#                             value_count_total += text.count(real_value)
#                             value_count_per_document += 1

#                     info_values[value] = {'value_count_per_document': value_count_per_document, 'value_count_total': value_count_total}
                    
#                     data = data_new
                        
#                 elif type_data_field == 'list':
#                     raise ValueError('NOT IMPLEMENTED')
#             # if the filter is 'number'
#             elif obj_filter['type'] == 'number':
#                 # check if a specific number is requested
#                 result_positive = regex_filter_numbers_positive.search(value)
#                 result_negative = regex_filter_numbers_negative.search(value)
#                 if result_positive != None:
#                     number = float(result_positive.group(1))
#                     data = [item for item in data if item[obj_filter['data_field']] == number]
#                 elif result_negative != None:
#                     number = float(result_negative.group(1))
#                     data = [item for item in data if item[obj_filter['data_field']] == number]
#                 else:
#                     result_lt = regex_filter_numbers_lt.search(value)
#                     if result_lt != None:
#                         number = float(result_lt.group(1))
#                         data = [item for item in data if item[obj_filter['data_field']] < number]

#                     result_lte = regex_filter_numbers_lte.search(value)
#                     if result_lte != None:
#                         number = float(result_lte.group(1))
#                         data = [item for item in data if item[obj_filter['data_field']] <= number]

#                     result_gt = regex_filter_numbers_gt.search(value)
#                     if result_gt != None:
#                         number = float(result_gt.group(1))
#                         data = [item for item in data if item[obj_filter['data_field']] > number]
                    
#                     result_gte = regex_filter_numbers_gte.search(value)
#                     if result_gte != None:
#                         number = float(result_gte.group(1))
#                         data = [item for item in data if item[obj_filter['data_field']] >= number]
#     return data, info_values

def filter_data_tags(data, list_tags, request):
    # get the database objects for each tag
    queryset_tags = m_Tag.objects.filter(name__in=list_tags, key_corpus=get_current_corpus(request)).prefetch_related('m2m_entity')
    # for each tag
    for db_obj_tag in queryset_tags:
        # get all entities for the current tag 
        list_ids = [entity.id_item for entity in db_obj_tag.m2m_entity.all()]
        # only keep items, which id is in the entities list
        data = [item for item in data if str(item[get_setting('id', request=request)]) in list_ids]

    return data

def add_tag(obj, data, request):
    [db_obj_tag, created_tag] = get_or_create_tag(obj['tag'], defaults={'color': obj['color']}, request=request)

    entities = []
    if obj['ids'] == 'all':
        if get_setting('data_type', request=request) == 'database':
            entities = data
        else:
            entities = [str(item[get_setting('id', request=request)]) for item in data]
    else:
        if get_setting('data_type', request=request) == 'database':
            entities = list(model_custom.objects.filter(post_id_str__in=obj['ids']))
        else:
            entities = obj['ids']

    if get_setting('data_type', request=request) == 'database':
        n = 900
        chunks = [entities[x:x+n] for x in range(0, len(entities), n)]
        for chunk in chunks:
            db_obj_tag.m2m_custom_model.add(*chunk)
    else:
        index_missing_entities(entities, request)

        n = 900
        chunks = [entities[x:x+n] for x in range(0, len(entities), n)]
        for chunk in chunks:
            db_obj_entities = m_Entity.objects.filter(id_item__in=chunk, key_corpus=get_current_corpus(request))
            db_obj_tag.m2m_entity.add(*db_obj_entities)

    if db_obj_tag.color != obj['color']:
        db_obj_tag.color = obj['color']
        db_obj_tag.save()

    return {'created_tag': created_tag, 'tag': {'id': db_obj_tag.id, 'name': db_obj_tag.name, 'color': db_obj_tag.color} }

def index_missing_entities(entities, request):
    queryset = m_Entity.objects.filter(key_corpus=get_current_corpus(request))
    set_new_entities = set(entities)

    set_new_entities.difference_update({entity.id_item for entity in queryset})

    if len(set_new_entities) > 0:
        m_Entity.objects.bulk_create([m_Entity(id_item=entity, key_corpus=get_current_corpus(request)) for entity in set_new_entities])


def get_tags_filtered_items(list_ids, request):
    if get_setting('data_type', request=request) == 'database':
        list_tags = []
        n = 900
        chunks = [list_ids[x:x+n] for x in range(0, len(list_ids), n)]
        for chunk in chunks:
            list_tags += m_Tag.objects.filter(m2m_custom_model__in=chunk, key_corpus=get_current_corpus(request)).distinct()

        dict_ordered_tags = collections.OrderedDict()
        for tag in list_tags:
            if tag.name not in dict_ordered_tags:
                dict_ordered_tags[tag.name] = {'id': tag.id, 'name': tag.name, 'color': tag.color, 'is_selected': str(tag.id) in request.session[get_current_corpus(request)]['viewer__viewer__selected_tags']}
        return list(dict_ordered_tags.values())
    else:
        n = 900
        chunks = [list_ids[x:x+n] for x in range(0, len(list_ids), n)]

        list_tags = []
        for chunk in chunks:
            list_tags += m_Tag.objects.filter(m2m_entity__id_item__in=chunk, key_corpus=get_current_corpus(request)).distinct()

        dict_ordered_tags = collections.OrderedDict()
        for tag in list_tags:
            if tag.name not in dict_ordered_tags:
                dict_ordered_tags[tag.name] = {'id': tag.id, 'name': tag.name, 'color': tag.color, 'is_selected': str(tag.id) in request.session[get_current_corpus(request)]['viewer__viewer__selected_tags']}

        return list(dict_ordered_tags.values())

def replacement(matchobj):
    return '<span style="background-color: lightblue">'+matchobj.group(1)+'</span>'

def add_tags(data, request):
    if get_setting('data_type', request=request) != 'database':
        list_ids = [item[get_setting('id', request=request)] for item in data]
        db_obj_entities = m_Entity.objects.filter(id_item__in=list_ids, key_corpus=get_current_corpus(request)).prefetch_related('viewer_tags')
        dict_entities = {entity.id_item: entity for entity in db_obj_entities}

        for item in data:
            try:
                item['viewer_tags'] = dict_entities[str(item[get_setting('id', request=request)])].viewer_tags.all()
            except KeyError:
                # if there is no entity entry in the database
                item['viewer_tags'] = []


            # for obj_filter in get_setting('filters', request=request):
                # filter the data by the current filter+
                # print(obj_filter)

                # values = request.session[get_current_corpus(request)]['viewer__viewer__filter_custom'][obj_filter['data_field']]

                # for value in values:
                #     if obj_filter['type'] == 'contains':
                #         # get the type (string, list) of the data-field
                #         type_data_field = get_setting('data_fields', request=request)[obj_filter['data_field']]['type']
                #         if type_data_field == 'string' or type_data_field == 'text':
                #             # return only items which contain all the values
                #             case_sensitivity = value[0]
                #             real_value = value[2:]
                #             if case_sensitivity == 'i':
                #                 item[obj_filter['data_field']] = re.sub('('+real_value+')', replacement, item[obj_filter['data_field']])
                #             else:
                #                 item[obj_filter['data_field']] = re.sub('('+real_value+')', replacement, item[obj_filter['data_field']])

                                # data = [item for item in data if real_value in str(item[obj_filter['data_field']])]
                # data = filter_data(request, data, obj_filter)
