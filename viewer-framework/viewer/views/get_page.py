from .shared_code import set_sessions, load_data, get_or_create_tag, \
    get_items_by_indices, get_item_by_ids, glob_manager_data, get_current_corpus, get_filters_if_not_empty
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
import csv
import importlib
from django.core.exceptions import FieldError
from django.db import connection


regex_filter_numbers_negative = re.compile('(?<![>|\.|>=|<=|<|<|0|1|2|3|4|5|6|7|8|9|0])(-[0-9]+\.?[0-9]*)')
regex_filter_numbers_positive = re.compile('(?<![>|\.|>=|<=|<|<|0|1|2|3|4|5|6|7|8|9|0|-])([0-9]+\.?[0-9]*)')
regex_filter_numbers_lt = re.compile('<(-?[0-9]+\.?[0-9]*)')
regex_filter_numbers_lte = re.compile('<=(-?[0-9]+\.?[0-9]*)')
regex_filter_numbers_gt = re.compile('>(-?[0-9]+\.?[0-9]*)')
regex_filter_numbers_gte = re.compile('>=(-?[0-9]+\.?[0-9]*)')

def get_page(request, id_corpus):
##### handle session entries
    start_total = time.perf_counter()

    if not set_sessions(request, id_corpus):
        raise Http404("Corpus does not exist")

    # id_corpus = get_current_corpus(request)

    if glob_manager_data.has_corpus_secret_token(id_corpus):
        try:
            secret_token = request.session[id_corpus]['viewer__secret_token']
        except KeyError:
            secret_token = None
        if not glob_manager_data.is_secret_token_valid(id_corpus, secret_token):
            return redirect('viewer:add_token')    
##### load data and apply filters
    start = time.time()
    if glob_manager_data.get_setting_for_corpus('data_type', id_corpus) == 'database':
        list_ids, info_filter_values = get_filtered_data_database(request)
    else:
        list_ids, info_filter_values = get_filtered_data(request)
    print('get_filtered_data {}'.format(format(time.time() - start, '.3f')))
##### check if has token for editing
    has_access_to_editing = glob_manager_data.get_has_access_to_editing(id_corpus, request)  
##### handle post requests
    if request.method == 'POST':
        response = {}
        obj = json.loads(request.body.decode("utf-8"))
        if obj['task'] == 'add_tag':
            if has_access_to_editing:
                response['data'] = add_tag(obj, list_ids, request)
        elif obj['task'] == 'export_data':
            response = export_data(obj, data, request)
        elif obj['task'] == 'reload_settings':
            # if has_access_to_editing:
            if glob_manager_data.reload_settings(id_corpus) == None:
                response['success'] = False
            else:
                response['success'] = True
        elif obj['task'] == 'reindex_corpus':
            # if has_access_to_editing:
            try:
                glob_manager_data.reindex_corpus(obj['id_corpus'], obj['class_handle_index'])
            except:
                glob_manager_data.reindex_corpus(id_corpus, obj['class_handle_index'])
        elif obj['task'] == 'get_number_of_indexed_items':
            if id_corpus in glob_manager_data.dict_exceptions:
                response['exception_occured'] = True
            else:
                response['exception_occured'] = False

            response['number_of_indexed_items'] = glob_manager_data.get_number_of_indexed_items(obj['id_corpus'])
            response['state_loaded'] = glob_manager_data.get_state_loaded(obj['id_corpus'])
        elif obj['task'] == 'delete_corpus':
            if has_access_to_editing:
                glob_manager_data.delete_corpus(id_corpus, obj['keep_settings_file'])
        elif obj['task'] == 'create_variable_glob_selected_items':
            response['glob_selected_items'] = create_variable_glob_selected_items(id_corpus, list_ids)

        return JsonResponse(response)
##### page the dataset
    start = time.time()
    # list_tags = []
    list_tags = get_tags_filtered_items(list_ids, request)
    print('get_tags_filtered_items {}'.format(format(time.time() - start, '.3f')))

    start = time.time()
    list_ids = sort_by_columns(request, list_ids)
    print('sort_by_columns {}'.format(format(time.time() - start, '.3f')))

    start = time.time()
    # paginator = Paginator(range(0, get_setting('page_size', request=request))
    paginator = Paginator(list_ids, glob_manager_data.get_setting_for_corpus('page_size', id_corpus))

    print(glob_manager_data.dict_corpora[id_corpus]['size'])

    # if get_filters_if_not_empty(request, id_corpus) == None:
    #     paginator.count = glob_manager_data.dict_corpora[id_corpus]['size']

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
    print('paging {}'.format(format(time.time() - start, '.3f')))

    start_loading = time.perf_counter()

    if glob_manager_data.get_setting_for_corpus('data_type', id_corpus) != 'database':
        data = glob_manager_data.get_items(id_corpus, page_current)
    else:
        data = page_current

    print('loading time: '+str(round(float(time.perf_counter() - start_loading) * 1000, 2))+'ms')

    add_tags(data, request)
##### handle post requests
    context = {}
    context['settings'] = glob_manager_data.get_settings_for_corpus(id_corpus)
    context['data'] = data
    context['id_corpus'] = id_corpus
    context['has_access_to_editing'] = has_access_to_editing

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

def create_variable_glob_selected_items(id_corpus, list_ids):
    dict_selected_items = {}
    field_id = glob_manager_data.get_setting_for_corpus('id', id_corpus)

    if glob_manager_data.get_setting_for_corpus('data_type', id_corpus) == 'database':
        for item in list_ids:
            id_item = str(getattr(item, field_id))
            id_item_internal = item.id

            dict_selected_items[id_item+'-'+str(id_item_internal)] = {
                'id_item': id_item,
                'viewer__id_item_internal': id_item_internal
            }
    else:
        field_id_internal = 'viewer__id_item_internal'

        n = 10
        chunks = [list_ids[x:x+n] for x in range(0, len(list_ids), n)]
        for chunk in chunks:
            list_items = glob_manager_data.get_items(id_corpus, chunk)
            for item in list_items:
                id_item = str(item[field_id])
                id_item_internal = item[field_id_internal]
                dict_selected_items[id_item+'-'+str(id_item_internal)] = {
                    'id_item': id_item,
                    'viewer__id_item_internal': id_item_internal
                }

    # for id_ in list_ids:
    #     print(glob_manager_data.get_item(id_corpus, id_))
        # print(id_)
    return dict_selected_items

def function_sort(id_item, id_corpus, field):
    return glob_manager_data.get_item(id_corpus, id_item)[field]

def sort_by_columns(request, list_ids):
    id_corpus = get_current_corpus(request)

    list_sorted_columns = request.session[id_corpus]['viewer__viewer__sorted_columns']

    if glob_manager_data.get_setting_for_corpus('data_type', id_corpus) == 'database':
        for sorted_column in reversed(list_sorted_columns):
            # print(sorted_column)
            # print(list_ids)
            sign = '-' if sorted_column['order'] == 'desc' else ''
            # print(sign+sorted_column['field'])
            list_ids = list_ids.order_by(sign+sorted_column['field'])
    else:
        for sorted_column in reversed(list_sorted_columns):
            is_reversed = False
            if sorted_column['order'] == 'desc':
                is_reversed = True

            list_ids = sorted(list_ids, key=lambda id_item: function_sort(id_item, id_corpus, sorted_column['field']), reverse=is_reversed)
            print(sorted_column)
    return list_ids

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

def get_filtered_data_database(request):
    info_filter_values = {}
    id_corpus = get_current_corpus(request)

    module_custom = importlib.import_module(glob_manager_data.get_setting_for_corpus('app_label', id_corpus)+'.models')
    model_custom = getattr(module_custom, glob_manager_data.get_setting_for_corpus('model_name', id_corpus))

    queryset_entities = model_custom.objects.prefetch_related(
        *glob_manager_data.get_setting_for_corpus('database_prefetch_related', id_corpus)
    ).select_related(
        *glob_manager_data.get_setting_for_corpus('database_select_related', id_corpus)
    ).filter(
        **glob_manager_data.get_setting_for_corpus('database_filters', id_corpus)
    ).prefetch_related('corpus_viewer_tags')

    #
    # FILTER BY TAGS 
    #
    values_filter_tags = request.session[id_corpus]['viewer__viewer__filter_tags']
    if len(values_filter_tags) > 0:
        for name_tag in values_filter_tags:
            queryset_entities = queryset_entities.filter(corpus_viewer_tags__name=name_tag)

    for obj_filter in glob_manager_data.get_setting_for_corpus('filters', id_corpus):
        type_data_field = glob_manager_data.get_setting_for_corpus('data_fields', id_corpus)[obj_filter['data_field']]['type']
        info_values = {}
        values = request.session[id_corpus]['viewer__viewer__filter_custom'][obj_filter['data_field']]

        if type_data_field == 'number':
            for value in values:
                info_values[value] = {'value_count_per_document': 0, 'value_count_total': 0}
                queryset_entities = queryset_entities.filter(**{obj_filter['data_field']+'__exact': value})
        if type_data_field == 'boolean':
            for value in values:
                info_values[value] = {'value_count_per_document': 0, 'value_count_total': 0}
                queryset_entities = queryset_entities.filter(**{obj_filter['data_field']: value})
        else:
            for value in values:
                real_value = value[2:]
                info_values[value] = {'value_count_per_document': 0, 'value_count_total': 0}
                queryset_entities = queryset_entities.filter(**{obj_filter['data_field']+'__icontains': real_value})

        info_filter_values[obj_filter['data_field']] = info_values

    return queryset_entities, info_filter_values

def get_filtered_data(request):
    info_filter_values = {}
    id_corpus = get_current_corpus(request)

    dict_filters = get_filters_if_not_empty(request, id_corpus)
    if dict_filters == None:
        # print('######### ALL IDS')   
        return glob_manager_data.get_all_ids_for_corpus(id_corpus, glob_manager_data.get_settings_for_corpus(id_corpus)), info_filter_values
    else:
        bytes_dict_filters = json.dumps(dict_filters, sort_keys=True).encode()
        hash_custom = hashlib.sha1(bytes_dict_filters).hexdigest()
        # fails if the user has no hash stored
        try:
            # checks if the hash corresponds to the last hash
            if hash_custom == request.session[id_corpus]['viewer__last_hash']:
                # print('######### LAST RESULT')    
                pass
                return request.session[id_corpus]['viewer__last_result']
        except:
            pass
    
    # print('######### NEW RESULT')    
    # print(hash_customs)
    list_data = None
    #
    # FILTER BY TAGS 
    #
    values_filter_tags = request.session[id_corpus]['viewer__viewer__filter_tags']
    print(values_filter_tags)
    if len(values_filter_tags) > 0:
        print('TAGSSSS')
        
                # list_data = list_data.filter(tags__in=m_Tag.objects.get(key_corpus=id_corpus, name=name_tag).m2m_entity.all())

            # print()
            # raise NotImplementedError()
            # for tag in values_filter_tags:
            #     data = data.filter(viewer_tags__name=tag)
            # list_data 
            # filter the data by tags
        list_data = filter_data_tags(values_filter_tags, id_corpus)

    #
    # FILTERS
    #

    for obj_filter in glob_manager_data.get_setting_for_corpus('filters', id_corpus):
            # data = data.filter(**{obj_filter['data_field']+'__icontains': value})
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
        if glob_manager_data.get_setting_for_corpus('data_type', id_corpus) != 'database':
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
    if len(values) == 0:
        info_values = {value:{'value_count_per_document': 0, 'value_count_total': 0} for value in values}
    else:
        info_values = {value:{'value_count_per_document': 0, 'value_count_total': 0} for value in values}
        skipped = False
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
        elif type_data_field == 'boolean':
            for value in values:
                print(value)
                list_data_new = glob_manager_data.get_handle_index(id_corpus).get_boolean(obj_filter['data_field'], value)
                
                if list_data == None:
                    list_data = sorted(list_data_new)
                else:
                    set_tmp = frozenset(list_data_new)
                    list_data = [x for x in list_data if x in set_tmp]


    if list_data == None:
        list_data = []
    return list_data, info_values, skipped

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

def filter_data_tags(list_tags, id_corpus):
    set_ids_result = None
    # get the database objects for each tag
    queryset_tags = m_Tag.objects.filter(name__in=list_tags, key_corpus=id_corpus).prefetch_related('m2m_entity')
    # for each tag
    for db_obj_tag in queryset_tags:
        # get all entities for the current tag 
        set_ids = {entity.id_item_internal for entity in db_obj_tag.m2m_entity.all()}

        if set_ids_result == None:
            set_ids_result = set_ids
        else:
            set_ids_result.intersection_update(set_ids)
        # only keep items, which id is in the entities list
        # data = [item for item in data if str(item[glob_manager_data.get_setting_for_corpus('id', id_corpus)]) in list_ids]

    return sorted(set_ids_result)

def add_tag(obj, list_ids, request):
    id_corpus = get_current_corpus(request)
    # print('################################################')
    # print(obj)
    [db_obj_tag, created_tag] = get_or_create_tag(obj['tag'], defaults={'color': obj['color']}, request=request)

    if glob_manager_data.get_setting_for_corpus('data_type', id_corpus) == 'database':
        print(obj)
        if obj['ids'] == 'all':
            related_name = glob_manager_data.get_setting_for_corpus('database_related_name', id_corpus)
            getattr(db_obj_tag, related_name).add(*list_ids)
        else:
            module_custom = importlib.import_module(glob_manager_data.get_setting_for_corpus('app_label', id_corpus)+'.models')
            model_custom = getattr(module_custom, glob_manager_data.get_setting_for_corpus('model_name', id_corpus))

            queryset = model_custom.objects.filter(id__in=[x['viewer__id_item_internal'] for x in obj['ids']])

            related_name = glob_manager_data.get_setting_for_corpus('database_related_name', id_corpus)
            getattr(db_obj_tag, related_name).add(*queryset)

        return {'created_tag': created_tag, 'tag': {'id': db_obj_tag.id, 'name': db_obj_tag.name, 'color': db_obj_tag.color} }
    else:
        entities = []
        if obj['ids'] == 'all':
            for id_item in list_ids:
                obj_item = glob_manager_data.get_item(id_corpus, id_item)
                entities.append({
                    'id_item': str(obj_item[glob_manager_data.get_setting_for_corpus('id', id_corpus)]),
                    'viewer__id_item_internal': id_item
                })
        else:
            entities = obj['ids']

        index_missing_entities(entities, id_corpus)

        n = 900
        chunks = [entities[x:x+n] for x in range(0, len(entities), n)]
        for chunk in chunks:
            chunk = [foo['id_item'] for foo in chunk]
            db_obj_entities = m_Entity.objects.filter(id_item__in=chunk, key_corpus=id_corpus)
            print(db_obj_entities)
            db_obj_tag.m2m_entity.add(*db_obj_entities)

        if db_obj_tag.color != obj['color']:
            db_obj_tag.color = obj['color']
            db_obj_tag.save()

        return {'created_tag': created_tag, 'tag': {'id': db_obj_tag.id, 'name': db_obj_tag.name, 'color': db_obj_tag.color} }

def index_missing_entities(entities, id_corpus):
    
    queryset = m_Entity.objects.filter(key_corpus=id_corpus)

    list_tupels = []
    for entity in entities:
        list_tupels.append((str(entity['id_item']), entity['viewer__id_item_internal']))
    set_new_entities = set(list_tupels)
    # set_new_entities = {entity['id_item_internal'] for entity in entities}

    # set_new_entities.difference_update(tuple(entity.id_item, entity.id_item_internal for entity in queryset))
    set_new_entities.difference_update({(entity.id_item, entity.id_item_internal) for entity in queryset})
    if len(set_new_entities) > 0:
        result = m_Entity.objects.bulk_create([m_Entity(id_item=entity[0], id_item_internal=entity[1], key_corpus=id_corpus) for entity in set_new_entities])

def get_tags_filtered_items(list_ids, request):
    id_corpus = get_current_corpus(request)

    # if glob_manager_data.get_number_of_indexed_items(id_corpus) == len(list_ids):
    #     list_tags = []
    #     for tag in m_Tag.objects.filter(key_corpus=id_corpus):
    #         list_tags.append({'id': tag.id, 'name': tag.name, 'color': tag.color, 'is_selected': str(tag.id) in request.session[id_corpus]['viewer__viewer__selected_tags']})
    #     return list_tags
    if glob_manager_data.get_setting_for_corpus('data_type', id_corpus) == 'database':
        list_tags = []

        try:
            if connection.vendor == 'postgresql':
                related_name = glob_manager_data.get_setting_for_corpus('database_related_name', id_corpus)

                list_tags = m_Tag.objects.filter(
                    **{
                        related_name + '__in': list_ids,
                        'key_corpus': id_corpus
                    }
                ).distinct()
            else:
                list_tags = m_Tag.objects.filter(key_corpus=id_corpus)

                # print(list_ids)
                # len(list_ids) 
                # n = 900
                # # print(list_ids)
                # list_entities = list_ids
                # chunks = [list_entities[x:x+n] for x in range(0, len(list_entities), n)]
                # for chunk in chunks:
                #     list_tags += m_Tag.objects.filter(corpus_viewer_items__in=chunk, key_corpus=id_corpus).distinct()
        except FieldError:
            pass

        dict_ordered_tags = collections.OrderedDict()
        for tag in list_tags:
            if tag.name not in dict_ordered_tags:
                dict_ordered_tags[tag.name] = {'id': tag.id, 'name': tag.name, 'color': tag.color, 'is_selected': str(tag.id) in request.session[id_corpus]['viewer__viewer__selected_tags']}
        return list(dict_ordered_tags.values())
    else:
        if glob_manager_data.get_number_of_indexed_items(id_corpus) == len(list_ids):
            list_tags = m_Tag.objects.filter(key_corpus=id_corpus, m2m_entity__isnull=False).distinct()
        else:
            n = 900
            chunks = [list_ids[x:x+n] for x in range(0, len(list_ids), n)]
            list_tags = []
            for chunk in chunks:
                list_tags += m_Tag.objects.filter(m2m_entity__id_item_internal__in=chunk, key_corpus=id_corpus).distinct()

        dict_ordered_tags = collections.OrderedDict()
        for tag in list_tags:
            if tag.name not in dict_ordered_tags:
                dict_ordered_tags[tag.name] = {'id': tag.id, 'name': tag.name, 'color': tag.color, 'is_selected': str(tag.id) in request.session[id_corpus]['viewer__viewer__selected_tags']}

        return list(dict_ordered_tags.values())

def replacement(matchobj):
    return '<span style="background-color: lightblue">'+matchobj.group(1)+'</span>'

def add_tags(data, request):
    id_corpus = get_current_corpus(request)

    if glob_manager_data.get_setting_for_corpus('data_type', id_corpus) != 'database':
        list_ids = [item[glob_manager_data.get_setting_for_corpus('id', id_corpus)] for item in data]
        # print(list_ids)
        db_obj_entities = m_Entity.objects.filter(id_item__in=list_ids, key_corpus=id_corpus).prefetch_related('viewer_tags')
        # print(db_obj_entities)
        dict_entities = {entity.id_item: entity for entity in db_obj_entities}
        # print(dict_entities)
        for item in data:
            try:
                id_item = str(item[glob_manager_data.get_setting_for_corpus('id', id_corpus)])
                item['viewer_tags'] = dict_entities[id_item].viewer_tags.all()
            except KeyError:
                # if there is no entity entry in the database
                item['viewer_tags'] = []


            # for obj_filter in get_setting('filters', request=request):
                # filter the data by the current filter+
                # print(obj_filter)

                # values = request.session[id_corpus]['viewer__viewer__filter_custom'][obj_filter['data_field']]

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
    else:
        try:
            for item in data:
                item.viewer_tags = item.corpus_viewer_tags.all()
        except AttributeError:
            for item in data:
                item.viewer_tags = []
