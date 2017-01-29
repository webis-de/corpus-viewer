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
    data.viewer__page = glob_current_page;
    data.viewer__columns = JSON.stringify(glob_columns);

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
function start_loading()
{
    $('#wrapper_loading').show();
}

function stop_loading()
{
    $('#wrapper_loading').hide();
}

function remove_element_from_array(array, element)
{
    let index = array.indexOf(element);
    if(index > -1)
    {
        array.splice(index, 1);
    }
}

function add_tag_marker(tag_id, tag_name, tag_color)
{
    remove_tag_marker(tag_id)
    $('.wrapper_tags.tag_'+tag_id).append(function() {
        return '<div class="tag_marker" data-tag_id="'+tag_id+'" style="background-color: '+tag_color+'" data-toggle="tooltip" title="'+tag_name+'"></div>'
    });
}

function remove_tag_marker(tag_id)
{
    $('.tag_marker[data-tag_id="'+tag_id+'"]').remove();
}

function add_tag_to_tags_list(id, name, color)
{
    list_tags = []
    $('#wrapper_tags_filtered_items input').each(function(index, element) {
        let elem = $(element)
        let is_selected = elem.prop('checked')
        list_tags.push({id: elem.data('tag_id'), name: elem.data('tag_name'), color: elem.data('tag_color'), is_selected: is_selected})
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

function update_tags_list(tags)
{
    let content = '';
    for (let i = 0; i < tags.length; i++) {
        let tag = tags[i];
        let checked = ''
        if(tag.is_selected)
        {
            checked = 'checked'
            add_tag_marker(tag.id, tag.name, tag.color)
        }

        content +=  '<tr class="tr_tag">'+
                        '<td>'+
                            '<input type="checkbox" class="checkbox_tag_selection" '+checked+' data-tag_id="'+tag.id+'" data-tag_name="'+tag.name+'" data-tag_color="'+tag.color+'">'+
                        '</td>'+
                        '<td class="td_tag_selection" data-tag_id="'+tag.id+'">'+
                            '<div class="tag_marker" style="background-color: '+tag.color+'"></div>'+
                        '</td>'+
                        '<td data-tag_id="'+tag.id+'">'+
                            '<span class="label label-default">'+tag.name+'</span>'+
                        '</td>'+
                    '</tr>';
    }
    $('#wrapper_tags_filtered_items').html(content);
    update_checkbox_select_all('checkbox_tag_selection', 'checkbox_tag_selection_all')
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
        }
    });
}


function update_ui()
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
    $('#info_number_of_items').text('filtered items: '+glob_count_entries.toLocaleString()+' ('+glob_count_pages.toLocaleString()+' page(s))');

    $('.input_select_item').each(function(index, element) {
        const elem = $(element)
        if(elem.data('id_item') in glob_selected_items)
        {
            elem.prop('checked', true)
        }
    });
    update_checkbox_select_all('input_select_item', 'input_select_all_items')
}