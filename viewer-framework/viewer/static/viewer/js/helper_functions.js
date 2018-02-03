// recommendations ////////////////////////////////////////////////////////////////////////////
function create_filter_active(value, data_field, info_filter_values)
{
    // if is contains filter
    if(value.startsWith('s_') || value.startsWith('i_'))
    {
        is_case_sensitive = value.substring(0, 1) == 's';
        value_real = value.substring(2);

        return create_filter_active_contains(value, data_field, value_real, is_case_sensitive, info_filter_values)
    } else {
        return create_filter_active_number(value, data_field, info_filter_values)
    }
}

function create_filter_active_contains(value, data_field, value_real, is_case_sensitive, info_filter_values)
{
    let template_case_sensitivity = '<span class="case_sensitivity bg-faded">aA</span>';

    let template_info_filter_values = glob_template_info_filter_values_contains
        .replace('PLACEHOLDER_VALUE_COUNT_TOTAL', info_filter_values.value_count_total)
        .replace('PLACEHOLDER_VALUE_COUNT_PER_DOCUMENT', info_filter_values.value_count_per_document);

    if(is_case_sensitive == false)
    {
        template_case_sensitivity = '';
    }

    return glob_template_filter_active_contains
        .replace('PLACEHOLDER_VALUE_REAL', value_real)
        .replace(/PLACEHOLDER_VALUE/g, value)
        .replace('PLACEHOLDER_DATA_FIELD', data_field)
        .replace('PLACEHOLDER_TEMPLATE_CASE_SENSITIVITY', template_case_sensitivity)
        .replace('PLACEHOLDER_TEMPLATE_INFO_FILTER_VALUES', template_info_filter_values)
}
function create_filter_active_number(value, data_field, info_filter_values)
{
    let template_info_filter_values = glob_template_info_filter_values_number
        .replace('PLACEHOLDER_VALUE_COUNT_TOTAL', info_filter_values.value_count_total)
        .replace('PLACEHOLDER_VALUE_COUNT_PER_DOCUMENT', info_filter_values.value_count_per_document);

    return glob_template_filter_active_number
        .replace(/PLACEHOLDER_VALUE/g, value)
        .replace('PLACEHOLDER_DATA_FIELD', data_field)
        .replace('PLACEHOLDER_TEMPLATE_INFO_FILTER_VALUES', template_info_filter_values)
}

function update_info_selected_items()
{
    const count_selected_items = Object.keys(glob_selected_items).length;
    // $('#info_selected_items span').text(count_selected_items)
    $('[data-inject="count_selected_rows"]').text(count_selected_items);
}

function update_checkbox_select_all(checkbox_class, checkbox_id)
{
    if($('.'+checkbox_class+':checked').length == $('.'+checkbox_class).length)
    {
        $('#'+checkbox_id).prop('checked', true)
    } else {
        $('#'+checkbox_id).prop('checked', false)
    }
}

function refresh_url()
{
    let data = {};
    // data.viewer__current_corpus = glob_current_corpus;
    data.viewer__page = glob_current_page;
    data.viewer__columns = JSON.stringify(glob_columns);
    data.viewer__sorted_columns = JSON.stringify(glob_sorted_columns);
    data.viewer__filter_tags = JSON.stringify(glob_filter_tags);
    data.viewer__filter_custom = JSON.stringify(glob_filter_custom);

    let url_params = '';
    $.each(data, function(index, value) {
        url_params += index+'='+value+'&';
    });
    url_params += 'viewer__time='+Date.now();
    // TODO: pushState?
    // history.pushState(null, null, '?'+url_params);
    history.replaceState(null, null, '?'+url_params);

    return url_params
}
function start_mode_add_tag(tag)
{
    $('#alert_mode_add_tag').removeClass('hidden-xs-up');

    glob_mode_add_tag.status = 'active';
    glob_mode_add_tag.tag.id = tag.id;
    glob_mode_add_tag.tag.name = tag.name;
    glob_mode_add_tag.tag.color = tag.color;
}
function end_mode_add_tag()
{
    $('#alert_mode_add_tag').addClass('hidden-xs-up');

    glob_mode_add_tag.status = 'inactive';
    glob_mode_add_tag.tag.id = '';
    glob_mode_add_tag.tag.name = '';
    glob_mode_add_tag.tag.color = '';
}

function start_loading()
{
    $('#wrapper_loading').show();
    $('#table_entities .content .overlay').show()
}

function stop_loading()
{
    $('#wrapper_loading').hide();
    $('#table_entities .content .overlay').hide()
}

function remove_element_from_array(array, element)
{
    let index = array.indexOf(element);
    if(index > -1)
    {
        array.splice(index, 1);
    }
}

function add_tag_marker(id_tag, tag_name, tag_color)
{
    remove_tag_marker(id_tag)
    $('.wrapper_tags.tag_'+id_tag).append(function() {
        return '<div class="tag_marker" data-id_tag="'+id_tag+'" style="background-color: '+tag_color+'" data-title="'+tag_name+'" data-content="<i class=&quot;fa fa-times text-danger&quot; data-id_tag=&quot;'+id_tag+'&quot;></i>" title="'+tag_name+'"></div>'
        // return '<div class="tag_marker" data-id_tag="'+id_tag+'" style="background-color: '+tag_color+'" data-title="'+tag_name+'" data-content="<i class=&quot;fa fa-times text-danger link_delete_tag&quot; data-id_tag=&quot;'+id_tag+'&quot;></i>" title="'+tag_name+'"></div>'
    });
}

function remove_tag_marker(id_tag, id_item = undefined)
{
    if(id_item == undefined)
    {
        $('.tag_marker[data-id_tag="'+id_tag+'"]').remove();
    } else {
        $('#table_entities tr[data-id_item="'+id_item+'"] .tag_marker[data-id_tag="'+id_tag+'"]').remove();
    }
}

function add_tag_to_tags_list(id, name, color)
{
    list_tags = []
    $('#wrapper_tags_filtered_items input').each(function(index, element) {
        let elem = $(element)
        let is_selected = elem.prop('checked')
        list_tags.push({id: elem.data('id_tag'), name: elem.data('tag_name'), color: elem.data('tag_color'), is_selected: is_selected})
    })

    list_tags.push({id: id, name: name, color: color, is_selected: true})

    list_tags.sort(function(a, b) {
        if(a.name == b.name)
        {
            return 0
        } else if(a.name < b.name) {
            return -1
        } else {
            return 1
        }
    })
    update_tags_list(list_tags)
}

function update_tags_list(tags, update_session=true)
{
    glob_selected_tags = {}
    let content = '';
    for (let i = 0; i < tags.length; i++) {
        let tag = tags[i];
        let checked = ''
        if(tag.is_selected)
        {
            checked = 'checked'
            add_tag_marker(tag.id, tag.name, tag.color)
            glob_selected_tags[tag.id] = tag.id;
        }

        content +=  '<tr class="tr_tag">'+
                        '<td>'+
                            '<input type="checkbox" class="checkbox_tag_selection" '+checked+' data-id_tag="'+tag.id+'" data-tag_name="'+tag.name+'" data-tag_color="'+tag.color+'">'+
                        '</td>'+
                        '<td class="td_tag_selection" data-id_tag="'+tag.id+'">'+
                            '<div class="tag_marker" style="background-color: '+tag.color+'"></div>'+
                        '</td>'+
                        '<td data-id_tag="'+tag.id+'" class="tooltip_name_tag" title="'+tag.name+'">'+
                            '<span class="label label-default">'+tag.name+'</span>'+
                        '</td>'+
                    '</tr>';
    }
    $('#wrapper_tags_filtered_items').html(content);
    update_checkbox_select_all('checkbox_tag_selection', 'checkbox_tag_selection_all')

    if(update_session)
    {
        set_session_entry('viewer__selected_tags', glob_selected_tags)
    }
}

function set_session_entry(session_key, session_value, callback)
{
    let data = {};
    data.task = "set_session_entry";
    data.session_key = session_key;
    data.session_value = session_value;

    $.ajax({
        method: 'POST',
        contentType: 'application/json',
        headers: {'X-CSRFToken':$('input[name="csrfmiddlewaretoken"]').val()},
        data: JSON.stringify(data),
        success: function(result) {
            if(callback != undefined)
            {
                callback()
            }
        },
        error: function(result) {
            error_corpus_not_exists();
        }
    });
}

function hightlight_results(key, value)
{
    if(value.startsWith('s_') || value.startsWith('i_'))
    {
        is_case_sensitive = value.substring(0, 1) == 's';
        value_real = value.substring(2);

        let replace = '(' + value_real + ')';
        let flags = 'g';
        if(!is_case_sensitive)
        {
            flags += 'i';
        }

        let re = new RegExp(replace, flags);

        let query = '.row_viewer__item .column_' + key;

        if($(query + ' td').length != 0)
        {
            query += ' td';
        }
        else {
            query += ' span';
        }

        $(query).each(function(index, element) {
            let text = $(element).html();
            text = text.replace(re, '<span style="background-color:lightblue">$1</span>');

            $(element).html('');            
            $(element).html(text);
        });
    }
}


function get_filters_empty()
{
    if(Object.keys(glob_filter_tags).length > 0)
    {
        return false;
    }
    
    let is_empty = true;
    $.each(glob_filter_custom, function(i, element) {
        if(element.length > 0)
        {
            is_empty = false;
            return false;
        }
    });

    return is_empty;
}

function update_ui(info_filter_values)
{
    if(get_filters_empty())
    {
        $('#wrapper_info_filters').html(`
            <span class="float-right text-muted">No filters are active</span>
        `);
    } else {
        $('#wrapper_info_filters').html(`
            <span class="float-right text-muted"> Filters are active
                <a href="#" id="link_reset_filters">clear</a>
            </span>
        `);
    }

    if(glob_prev_page != undefined)
    {
        $('#info_paginator button[data-direction="left"]').prop('disabled', false);
    } else {
        $('#info_paginator button[data-direction="left"]').prop('disabled', true);
    }
    if(glob_next_page != undefined)
    {
        $('#info_paginator button[data-direction="right"]').prop('disabled', false);
    } else {
        $('#info_paginator button[data-direction="right"]').prop('disabled', true);
    }

    $('#input_page').val(glob_current_page)
    $('#info_number_of_items').text('Filtered items: '+glob_count_entries.toLocaleString()+' ('+glob_count_pages.toLocaleString()+' page(s))');

    // reset the tag filters
    $('#wrapper_tag_filter_active').html('');
    $.each(glob_filter_tags, function(index, tag) {
        let obj_tag = glob_dict_filter_tags[tag];
        $('#wrapper_tag_filter_active').append(glob_template_filter_active_tag
            .replace(/PLACEHOLDER_VALUE/g, obj_tag.name)
            .replace(/PLACEHOLDER_COLOR/g, obj_tag.color));
        // '<li data-tag="' + tag + '"><span class="badge badge-default">' + tag + ' <i class="fa fa-times" aria-hidden="true"></i></span></li>')
    });

    // reset the custom filters
    $.each(glob_filter_custom, function(key, value) {
        if(typeof(value[0]) == typeof(true))
        {
            $('button[data-data_field="'+key+'"][data-value="'+value[0]+'"]').addClass('active')
        } else {
            $('.viewer__column_filter_active[data-data_field="'+ key +'"]').html('');
            $.each(value, function(index, element) {
                $('.viewer__column_filter_active[data-data_field="'+ key +'"]').append(create_filter_active(element, key, info_filter_values[key][element]));
                hightlight_results(key, element)
            });
        }
    })

    update_checkbox_select_all('input_toggle_columns', 'input_toggle_columns_all')

    $('.input_select_item').each(function(index, element) {
        const elem = $(element)

        if(glob_selected_items.hasOwnProperty(elem.data('id_item') + '-' + elem.data('viewer__id_item_internal')))
        {
            elem.prop('checked', true)
            $('.row_viewer__item[data-id_item="'+elem.data('id_item')+'"]').addClass('table-info');
        }
    });
    update_checkbox_select_all('input_select_item', 'input_select_all_items')

    update_sorted_columns();

    update_info_selected_items();
}

function update_sorted_columns()
{
    $('#wrapper_columns_sorted').html('');
    $(glob_sorted_columns).each(function(index, element) {
        let asc = 'badge-primary';
        let desc = 'badge-secondary';

        if(element.order == 'desc')
        {
            asc = 'badge-secondary';
            desc = 'badge-primary';
        }
        let template_sorted_column_active = glob_template_sorted_column_active
            .replace('PLACEHOLDER_ID_COLUMN', element.field)
            .replace('PLACEHOLDER_COLUMN', element.field)
            .replace('PLACEHOLDER_ASC', asc)
            .replace('PLACEHOLDER_DESC', desc);

        const obj = $(template_sorted_column_active);
        if(index == 0) 
        {
            obj.find('[data-direction="up"]').addClass('invisible');
        } 
        if(index == glob_sorted_columns.length - 1)
        {
            obj.find('[data-direction="down"]').addClass('invisible');
        }

        $('#wrapper_columns_sorted').removeClass('d-none');
        $('#wrapper_columns_sorted').append(obj);

    });
}

function escape_html(text) {
    return text.replace(/&/g,'&amp;').replace(/"/g, "&quot;").replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

function error_corpus_not_exists()
{
    location.reload();
}

function reload()
{
    location.reload();
}