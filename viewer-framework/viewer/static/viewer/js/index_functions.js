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

function handle_remove_tag_from_filter(tag)
{
    index = glob_filter_tags.indexOf(tag);
    if(index > -1)
    {
        glob_filter_tags.splice(index, 1);
    }
    $('#list_filter_tags li[data-tag="' + tag + '"').remove();

    set_session_entry('viewer__filter_tags', glob_filter_tags, function() {
        glob_current_page = 1;
        load_current_page();
    })
}

function handle_recommendation_filter(input, wrapper_recommendation, func)
{
    let tag_name = input.val();
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
            }
        });
    }
}

function handle_click_on_recommendation_filter(recommendation, func)
{
    let wrapper_recommendation = recommendation.parent();
    let input_tag_names = wrapper_recommendation.parent().find('input');
    let tag_name = recommendation.data('tag_name');

    input_tag_names.val('');
    remove_wrapper_recommendation(wrapper_recommendation);
    input_tag_names.focus();

    if(func)
    {
        func(tag_name);
    }
}

function handle_reset_filters()
{
    glob_current_page = 1;
    glob_filter_tags = [];

    let input_toggle_columns_all = $('#input_toggle_columns_all')
    if(!input_toggle_columns_all.prop('checked'))
    {
        input_toggle_columns_all.prop('checked', true)
        input_toggle_columns_all.trigger('change')
    }

    load_current_page();
}

function handle_toggle_column_all(input)
{
    if(input.prop('checked'))
    {
        glob_columns = [];
        $('.input_toggle_columns').each(function(index, element) {
            let elem = $(element)
            elem.prop('checked', true)
            let column = elem.data('column')
            glob_columns.push(column);
            $('.column_'+column).show();
        })
    } else {
        glob_columns = [];
        $('.input_toggle_columns').each(function(index, element) {
            let elem = $(element)
            elem.prop('checked', false)
            let column = elem.data('column')
            $('.column_'+column).hide();
        })
    }
    set_session_entry('viewer__columns', glob_columns)
    refresh_url();
}

function handle_toggle_column(input)
{
    let column = input.data('column')
    if(input.prop('checked'))
    {
        glob_columns.push(column);
        $('.column_'+column).show();
    } else {
        remove_element_from_array(glob_columns, column);
        $('.column_'+column).hide();
    }
    update_checkbox_select_all('input_toggle_columns', 'input_toggle_columns_all')
    set_session_entry('viewer__columns', glob_columns)
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
    update_checkbox_select_all('input_select_item', 'input_select_all_items')
    update_info_selected_items()
}

function handle_deselect_all_items(event)
{
    event.preventDefault()
    glob_selected_items = {}
    $('.input_select_item').prop('checked', false);
    update_checkbox_select_all('input_select_item', 'input_select_all_items')
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
            data.ids = [String(id_item)]
        }
    }

    let url_params = refresh_url();

    $.ajax({
        url: 'get_page?'+url_params,
        method: 'POST',
        contentType: 'application/json',
        headers: {'X-CSRFToken':$('input[name="csrfmiddlewaretoken"]').val()},
        data: JSON.stringify(data),
        success: function(result) {
            if(data.ids == 'all')
            {
                $('#table_entities .wrapper_tags').each(function(index, element) {
                    $(element).addClass('tag_'+result.data.tag.id)
                })
            } else {
                $.each(data.ids, function(index, id_item) {
                    $('#table_entities tr[data-id_item="'+id_item+'"] .wrapper_tags').addClass('tag_'+result.data.tag.id)
                })
                add_tag_marker(result.data.tag.id, result.data.tag.name, result.data.tag.color)
            }

            if(result.data.created_tag)
            {
                add_tag_to_tags_list(result.data.tag.id, result.data.tag.name, result.data.tag.color)
            }

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
        $('.checkbox_tag_selection').each(function(index, element) {
            let checkbox = $(element)
            let tag_id = checkbox.data('tag_id');
            let tag_name = checkbox.data('tag_name');
            let tag_color = checkbox.data('tag_color');
            glob_selected_tags[tag_id] = tag_id;
            add_tag_marker(tag_id, tag_name, tag_color);
            set_session_entry('viewer__selected_tags', glob_selected_tags)
            checkbox.prop('checked', true)
        })
    } else {
        $('.checkbox_tag_selection').each(function(index, element) {
            let checkbox = $(element)
            let tag_id = checkbox.data('tag_id');
            delete glob_selected_tags[tag_id];
            set_session_entry('viewer__selected_tags', glob_selected_tags)
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
        glob_selected_tags[tag_id] = tag_id;
        set_session_entry('viewer__selected_tags', glob_selected_tags)
        add_tag_marker(tag_id, tag_name, tag_color);
    } else {
        delete glob_selected_tags[tag_id];
        set_session_entry('viewer__selected_tags', glob_selected_tags)
        remove_tag_marker(tag_id);
    }
    update_checkbox_select_all('checkbox_tag_selection', 'checkbox_tag_selection_all')
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
            $('#table_entities .content .table').html(result.content)
            // console.log(result)
            glob_prev_page = result.previous_page_number;
            glob_next_page = result.next_page_number;
            glob_count_pages = result.count_pages;
            glob_count_entries = result.count_entries


            if(update_tags)
            {
                update_tags_list(result.tags_filtered_items, false);
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
            } else if(key == 'viewer__columns') {
                glob_columns = value
            } else if(key == 'viewer__filter_tags') {
                glob_filter_tags = value
            } else if(key == 'viewer__filter_custom') {
                glob_filter_custom = value
            }
        }
    })
}

function load_filters()
{
    $.each($('#json_filters').data('json_filters'), function(key, value){
        $(document).on(value.event, '#input_'+value.data_field, function(){
            let data_field = $(this).prop('name')
            let value = $(this).val()
            glob_filter_custom[data_field] = value
            
            set_session_entry('viewer__filter_custom', glob_filter_custom, function() {
                glob_current_page = 1;
                load_current_page();
            })
        });
    })
}
