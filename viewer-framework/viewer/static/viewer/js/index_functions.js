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

function handle_deselect_all_items(event)
{
    event.preventDefault()
    glob_selected_items = {}
    $('.input_select_item').prop('checked', false);
    update_input_select_all_items()
    update_info_selected_items()
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

function handle_click_link_add_tag(event, link)
{
    event.preventDefault();
    $('#modal_add_tag').data('id_item', link.data('id_item'));
    $('#modal_add_tag').modal('show')
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

function handle_shown_modal(event, modal)
{
    $('#input_name_new_tag').focus()
}

function handle_hide_modal(event, modal)
{
    modal.removeData('id_item');
}

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

function handle_change_displayed_tag_all(input)
{
    if(input.prop('checked'))
    {
        // glob_selected_tags[tag_id] = tag_id;
        $('.checkbox_tag_selection').each(function(index, element) {
            let checkbox = $(element)
            let tag_id = checkbox.data('tag_id');
            let tag_name = checkbox.data('tag_name');
            let tag_color = checkbox.data('tag_color');
            add_tag_marker(tag_id, tag_name, tag_color);
            checkbox.prop('checked', true)
        })
    } else {
        // delete glob_selected_tags[tag_id];
        $('.checkbox_tag_selection').each(function(index, element) {
            let checkbox = $(element)
            let tag_id = checkbox.data('tag_id');
            remove_tag_marker(tag_id);
            checkbox.prop('checked', false)
        })
    }
}

function handle_change_displayed_tag(checkbox)
{
    let tag_id = checkbox.data('tag_id');
    let tag_name = checkbox.data('tag_name');
    let tag_color = checkbox.data('tag_color');
    if(checkbox.prop('checked'))
    {
        // glob_selected_tags[tag_id] = tag_id;
        add_tag_marker(tag_id, tag_name, tag_color);
    } else {
        // delete glob_selected_tags[tag_id];
        remove_tag_marker(tag_id);
    }
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
                $.each($('.checkbox_tag_selection:checked'), function(index, element) {
                    add_tag_marker($(element).data('tag_id'), $(element).data('tag_name'), $(element).data('tag_color'));
                });
            }

            update_ui();
            stop_loading();
        },
    });
}
function load_page_parameters()
{
    $.each($('#json_url_params').data('json_url_params'), function(key, value){
        if(key.startsWith('viewer__'))
        {
            if(key == 'viewer__page')
            {
                glob_current_page = parseInt(value)
                console.log(glob_current_page)
            } else if(key == 'viewer__columns') {
                glob_columns = value
            }
        }
    })
}
