function add_tag(modal)
{
    const id_item = modal.data('id_item');
    let data = {}
    data.task = 'add_tag'
    data.tag = $('#input_name_new_tag').val()
    data.color = $('#input_color_tag').val()

    if($('#input_add_to_all_filtered_items').prop('checked'))
    {
        data.ids = 'all'
    } else {
        // if the modal was triggered by the button
        if(id_item == undefined)
        {
            data.ids = Object.keys(glob_selected_items)
        // if the modal was triggered by a link
        } else {
            data.ids = [id_item]
        }
    }

    $.ajax({
        method: 'POST',
        contentType: 'application/json',
        headers: {'X-CSRFToken':$('input[name="csrfmiddlewaretoken"]').val()},
        data: JSON.stringify(data),
        success: function(result) {
            modal.modal('hide');
        }
    })
}

function handle_change_add_to_all_filtered_items(input)
{
    let count = 0
    if(input.prop('checked'))
    {
        count = glob_count_entries
    } else {
        if($('#modal_add_tag').data('id_item') == undefined)
        {
            count = Object.keys(glob_selected_items).length
        } else {
            count = 1
        }
    }
    $('#info_count_selected_items').text(count)
}

function handle_shown_modal(event, modal)
{
    $('#input_name_new_tag').focus()
}

function handle_show_modal(event, modal)
{
    let count = 1
    if(modal.data('id_item') == undefined)
    {
        count = Object.keys(glob_selected_items).length
    }
    $('#info_count_selected_items').text(count)
}

function handle_hide_modal(event, modal)
{
    modal.removeData('id_item');
    // console.log('hidden')
}

function handle_click_link_add_tag(event, link)
{
    event.preventDefault();
    $('#modal_add_tag').data('id_item', link.data('id_item'));
    $('#modal_add_tag').modal('show')
}

function handle_rightclick_on_tr(event, tr)
{
    event.preventDefault(); 
    const id_item = tr.data('id_item')
    const elem = $('.input_select_item[data-id_item="'+id_item+'"]')
    if(elem.prop('checked'))
    {
        elem.prop('checked', false)
    } else {
        elem.prop('checked', true)
    }
    elem.trigger('change')
}

function update_input_select_all_items()
{
    if($('.input_select_item:checked').length == $('.input_select_item').length)
    {
        $('#input_select_all_items').prop('checked', true)
    } else {
        $('#input_select_all_items').prop('checked', false)
    }
}

function update_info_selected_items()
{
    $('#info_selected_items span').text(Object.keys(glob_selected_items).length)
}

function handle_deselect_all_items(event)
{
    event.preventDefault()
    glob_selected_items = {}
    $('.input_select_item').prop('checked', false);
    update_input_select_all_items()
    update_info_selected_items()
}

function handle_select_item(input)
{
    if(input.prop('checked'))
    {
        glob_selected_items[input.data('id_item')] = true;
    } else {
        delete glob_selected_items[input.data('id_item')];
    }
    update_input_select_all_items()
    update_info_selected_items()
}

function handle_selection_all_items(input)
{
    if(input.prop('checked'))
    {
        $('.input_select_item').prop('checked', true);
    } else {
        $('.input_select_item').prop('checked', false);
    }
    $('.input_select_item').trigger('change')
}

function handle_toggle_column(input)
{
	let column = input.data('column')
	if(input.prop('checked'))
	{
		glob_columns.push(column);
		set_session_entry('viewer__columns', glob_columns)
		$('.column_'+column).show();
	} else {
		remove_element_from_array(glob_columns, column);
		set_session_entry('viewer__columns', glob_columns)
		$('.column_'+column).hide();
	}
    refresh_url();
}

function handle_page_input(input)
{
    let page = input.val();
    if(page != '')
    {
        glob_current_page = page;
        load_current_page(false);
    }
}

function handle_pager_click(button)
{
    button.blur();
    if(button.data('target') == 'previous')
    {
        if(!glob_prev_page) return;
        glob_current_page = glob_prev_page;
    }
    else if(button.data('target') == 'first')
    {
        if(!glob_prev_page) return;
        glob_current_page = 1;
    }
    else if(button.data('target') == 'next')
    {
        if(!glob_next_page) return;
        glob_current_page = glob_next_page;
    }
    else if(button.data('target') == 'last')
    {
        if(!glob_next_page) return;
        glob_current_page = glob_count_pages;
    }
    load_current_page(false);
}

function load_current_page(update_tags = true)
{
    let url_params = refresh_url();

    $.ajax({
        url: 'get_page?'+url_params,
        beforeSend: function() {
            start_loading();
        },
        success: function(result) {
            $('#table_entities .content').html(result.content)
            // console.log(result)
            glob_prev_page = result.previous_page_number;
            glob_next_page = result.next_page_number;
            glob_count_pages = result.count_pages;
            glob_count_entries = result.count_entries

            if(update_tags)
            {
                update_tags_list(result.tags_filtered_items);
            } else {
                // $.each($('.checkbox_tag_selection:checked'), function(index, element) {
                //     add_tag_marker($(element).data('tag_id'), $(element).data('tag_name'), $(element).data('tag_color'));
                // });
            }

            update_ui();
            stop_loading();
        },
    });
}
function update_tags_list(tags)
{

    var content = '';
    for (var i = 0; i < tags.length; i++) {
        var tag = tags[i];
        content +=  '<tr class="tr_tag">'+
                        '<td>'+
                            '<input type="checkbox" class="checkbox_tag_selection" data-tag_id="'+tag.id+'" data-tag_name="'+tag.name+'" data-tag_color="'+tag.color+'">'+
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
    update_input_select_all_items()
}
function load_page_parameters()
{
    $.each($('#json_url_params').data('json_url_params'), function(key, value){
        if(key.startsWith('viewer__'))
        {
            if(key == 'viewer__page')
            {
                glob_current_page = value
            } else if(key == 'viewer__columns') {
                glob_columns = value
            }
        }
    })
}

function handle_card_click(link)
{
    set_session_entry('is_collapsed_'+link.attr('href').substr(1), !link.hasClass('show'));
}

function set_session_entry(session_key, session_value, callback)
{
    var data = {};
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

function refresh_url()
{
    var data = {};
    data.viewer__page = glob_current_page;
    data.viewer__columns = JSON.stringify(glob_columns);

    var url_params = '';
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