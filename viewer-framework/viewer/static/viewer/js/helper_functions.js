// recommendations ////////////////////////////////////////////////////////////////////////////
function trigger_tag_add_change(tag)
{
    $('#input_add_tag').val(tag.name);
    $('#button_start_mode_add_tag').data('tag', tag);

}
function trigger_tag_filter_change(tag)
{
    $('#list_filter_tags').append('<li data-tag="' + tag.name + '"><span class="badge badge-default">' + tag.name + ' <span class="fa fa-times"></span></span></li>')
    glob_filter_tags.push(tag.name);
    set_session_entry('viewer__filter_tags', glob_filter_tags, function() {
        glob_current_page = 1;
        load_current_page();
    })

}
function handle_click_on_recommendation(recommendation, input_tag_color)
{
    let wrapper_recommendation = recommendation.parent();
    let input_tag_name = wrapper_recommendation.parent().find('input');
    let tag_name = recommendation.data('tag_name');

    input_tag_name.val(tag_name);
    remove_wrapper_recommendation(wrapper_recommendation);


    if(input_tag_color)
    {
        let tag_color = recommendation.data('tag_color');
        input_tag_color.val(tag_color);
    }
}
function handle_recommendation(input, wrapper_recommendation)
{
    let tag_name = input.val().replace(' ', '-');
    if(tag_name == '')
    {
        remove_wrapper_recommendation(wrapper_recommendation);
    } else {
        let data = {};
        data.task = 'get_tag_recommendations';
        data.tag_name = tag_name;

        $.ajax({
            method: 'POST',
            contentType: 'application/json',
            headers: {'X-CSRFToken':$('input[name="csrfmiddlewaretoken"]').val()},
            data: JSON.stringify(data),
            success: function(result) {
                set_recommendations(wrapper_recommendation, $(result.data.array_recommendations));
            },
            error: function(result) {
                error_corpus_not_exists();
            }
        });
    }
}
function remove_wrapper_recommendation(wrapper_recommendation)
{
    wrapper_recommendation.hide();
    reset_recommendations(wrapper_recommendation);
}
function set_recommendations(wrapper_recommendation, array_recommendations)
{
    reset_recommendations(wrapper_recommendation);

    array_recommendations.each(function() {
        wrapper_recommendation.append(
            '<div class="recommendation" data-tag_id="'+this.id+'" data-tag_name="'+this.name+'" data-tag_color="'+this.color+'">'+
                '<div class="tag_marker_recommendation" style="background-color: '+this.color+';"></div>'+
            this.name+'</div>');
    });

    if(array_recommendations.length != 0)
    {
        wrapper_recommendation.show();
    } else {
        wrapper_recommendation.hide();
    }
}
function reset_recommendations(wrapper_recommendation)
{
    wrapper_recommendation.find('.recommendation').remove();
}

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
    $('#info_selected_items span').text(Object.keys(glob_selected_items).length)
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
    data.viewer__current_corpus = glob_current_corpus;
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
                        '<td data-id_tag="'+tag.id+'">'+
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

function update_ui(info_filter_values)
{
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
    $('#list_filter_tags').html('');
    for (let i = 0; i < glob_filter_tags.length; i++) {
        $('#list_filter_tags').append('<li data-tag="' + glob_filter_tags[i] + '"><span class="badge badge-default">' + glob_filter_tags[i] + ' <i class="fa fa-times" aria-hidden="true"></i></span></li>')
    }

    // reset the custom filters
    $.each(glob_filter_custom, function(key, value) {
        $('.viewer__column_filter_active[data-data_field="'+ key +'"]').html('');

        $.each(value, function(index, element) {
            $('.viewer__column_filter_active[data-data_field="'+ key +'"]').append(create_filter_active(element, key, info_filter_values[key][element]));
            hightlight_results(key, element)
        });
    })

    update_checkbox_select_all('input_toggle_columns', 'input_toggle_columns_all')

    $('.input_select_item').each(function(index, element) {
        const elem = $(element)

        if(glob_selected_items.hasOwnProperty(elem.data('id_item') + '-' + elem.data('id_item_internal')))
        {
            elem.prop('checked', true)
            $('.row_viewer__item[data-id_item="'+elem.data('id_item')+'"]').addClass('table-info');
        }
    });
    update_checkbox_select_all('input_select_item', 'input_select_all_items')
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