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
    let name_tag = tag.data('value');
    remove_element_from_array(glob_filter_tags, name_tag);

    set_session_entry('viewer__filter_tags', glob_filter_tags, function() {
        glob_current_page = 1;
        load_current_page();
    })
}

function handle_click_on_button_case_sensitivity(button)
{
    button.blur();
    if(button.hasClass('active'))
    {
        button.removeClass('active')
    } else {
        button.addClass('active')
    }
}

function handle_click_on_button_add_filter_contains(button)
{
    button.blur();
    let data_field = button.data('data_field');
    let input = $('#input_' + data_field);
    let value = input.val().trim();

    if(value == '') 
    {
        return;
    }

    let case_sensitivity = $('.viewer__button_case_sensitivity[data-data_field="'+ data_field +'"]');
    if(case_sensitivity.hasClass('active') == true)
    {
       value = 's_' + value;
    } else {
       value = 'i_' + value;
    }

    let is_unique = true;
    $.each($('.viewer__column_filter_active[data-data_field="'+ data_field +'"]>div'), function(key, div){
        // console.log($(div).data('value').toString(), value)
        if($(div).data('value').toString() == value)
        {
            is_unique = false;
            return false;
        }
    });

    if(is_unique == true)
    {
        // console.log(value)
        glob_filter_custom[data_field].push(value)
        set_session_entry('viewer__filter_custom', glob_filter_custom, function() {
            input.val('');
            glob_current_page = 1;
            load_current_page();
        })
    }
}
function handle_click_on_button_add_filter_number(button)
{
    button.blur();
    let data_field = button.data('data_field');
    let input = $('#input_' + data_field);
    let value = input.val().trim();

    if(value == '') 
    {
        return;
    }

    let is_unique = true;
    $.each($('.viewer__column_filter_active[data-data_field="'+ data_field +'"]>div'), function(key, div){
        // console.log($(div).data('value').toString(), value)
        if($(div).data('value').toString() == value)
        {
            is_unique = false;
            return false;
        }
    });

    if(is_unique == true)
    {
        // console.log(value)
        glob_filter_custom[data_field].push(value)
        set_session_entry('viewer__filter_custom', glob_filter_custom, function() {
            input.val('');
            glob_current_page = 1;
            load_current_page();
        })
    }
}

function handle_click_on_button_boolean(button)
{
    const data_field = button.data('data_field');
    const value = button.data('value');
    const value_other = value == true ? false : true;

    string_value_other = value_other == true ? 'true' : 'false';
    $('button[data-data_field="'+data_field+'"][data-value="'+string_value_other+'"]').removeClass('active')

    button.blur();
    if(button.hasClass('active'))
    {
        button.removeClass('active');
        glob_filter_custom[data_field] = []
    } else {
        button.addClass('active');
        glob_filter_custom[data_field] = [value]
    }

    set_session_entry('viewer__filter_custom', glob_filter_custom, function() {
        glob_current_page = 1;
        load_current_page();
    })
}

function handle_click_on_remove_filter_value(cross)
{
    let data_field = cross.data('data_field')
    let value = cross.data('value').toString();

    remove_element_from_array(glob_filter_custom[data_field], value)
    set_session_entry('viewer__filter_custom', glob_filter_custom, function() {
        glob_current_page = 1;
        load_current_page();
    })
}

function handle_reset_filters()
{
    glob_current_page = 1;
    glob_filter_tags = [];
    glob_dict_filter_tags = {};

    $.each(glob_filter_custom, function(key, value){
        glob_filter_custom[key] = [];
    })

    // let input_toggle_columns_all = $('#input_toggle_columns_all')
    // if(!input_toggle_columns_all.prop('checked'))
    // {
    //     input_toggle_columns_all.prop('checked', true)
    //     input_toggle_columns_all.trigger('change')
    // }

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
    $.event.trigger(glob_event_selected_items_update, glob_selected_items);
}

function handle_select_item(input, e)
{
    if(glob_mode_add_tag.status == 'inactive')
    {
        const id_item = input.data('id_item')
        const id_item_internal = input.data('viewer__id_item_internal')
        const obj_tmp = {'id_item': id_item, 'viewer__id_item_internal': id_item_internal};
        const obj_tmp_key = id_item + '-' + id_item_internal

        if(input.prop('checked'))
        {
            glob_selected_items[obj_tmp_key] = obj_tmp;

            $('.row_viewer__item[data-id_item="'+id_item+'"]').addClass('table-info');
        } else {
            $('.row_viewer__item[data-id_item="'+id_item+'"]').removeClass('table-info');

            delete glob_selected_items[obj_tmp_key]            
        }
        
        if(e.isTrigger == undefined)
        {
            $.event.trigger(glob_event_selected_items_update, glob_selected_items);
        }
        update_checkbox_select_all('input_select_item', 'input_select_all_items')
        update_info_selected_items()
    } else {
        if(input.prop('checked'))
        {
            input.prop('checked', false);
        } else {
            input.prop('checked', true);
        }
    }
}

function handle_click_on_button_select_all_items(button)
{
    button.blur();
    console.log('select')

    const data = {}
    data.task = 'create_variable_glob_selected_items';

    const url_params = refresh_url();

    $.ajax({
        url: glob_current_corpus+'/get_page?'+url_params,
        method: 'POST',
        contentType: 'application/json',
        headers: {'X-CSRFToken':$('input[name="csrfmiddlewaretoken"]').val()},
        data: JSON.stringify(data),
        success: function(result) {
            glob_selected_items = result.glob_selected_items
            $.event.trigger(glob_event_selected_items_update, glob_selected_items);
            $('.input_select_item').prop('checked', true)
            $('.row_viewer__item').addClass('table-info');
            update_checkbox_select_all('input_select_item', 'input_select_all_items')
            update_info_selected_items()
        },
        error: function(result) {
            error_corpus_not_exists();
        }
    })
}

function handle_click_on_button_deselect_all_items(button)
{
    button.blur();
    console.log('deselect')
    glob_selected_items = {}
    $.event.trigger(glob_event_selected_items_update, glob_selected_items);
    
    $('.input_select_item').prop('checked', false);
    $('.row_viewer__item').removeClass('table-info');
    update_checkbox_select_all('input_select_item', 'input_select_all_items')
    update_info_selected_items()
}

function handle_toggle_container_text(table)
{
    let rawText = table.find('td').data('content');
    let displayText = null;
    try {
        displayText = JSON.stringify(JSON.parse(rawText), null, 2);
    } catch (e) {
        displayText = rawText;
    }

    var row = $('.tr_container_text[data-id_item="'+table.data('id_item')+'"]');
    $('.popover_text').popover('hide');
    if(row.is(':visible'))
    {
        row.hide();
    } else {
        row.find('td div').html(
            '<pre class="m-0" style="font-family: sans-serif; font-size: 1rem; white-space: pre-wrap;">'+displayText+'</pre>'
        );
        row.show();
    }
}

function handle_mouseover_popover_text(table)
{
    var row = $('.tr_container_text[data-id_item="'+table.data('id_item')+'"]');
    if(!row.is(':visible'))
    {
        let popover = table.popover({
            placement: 'bottom',
            animation: false,
            html: true,
            template: '<div class="popover popover_text" role="tooltip"><div class="popover-arrow"></div><h3 class="popover-title"></h3><div class="popover-content"></div></div>',
            container: 'body',
            content: table.find('td').html(),
        })
        popover.popover('show');
    }
}

function handle_mouseout_popover_text(table)
{
    table.popover('dispose');
}

function delete_tag_from_item(id_item, id_tag)
{
    let data = {}
    data.task = 'delete_tag_from_item'
    data.id_item = id_item
    data.id_tag = id_tag

    $.ajax({
        url: '',
        method: 'POST',
        contentType: 'application/json',
        headers: {'X-CSRFToken':$('input[name="csrfmiddlewaretoken"]').val()},
        data: JSON.stringify(data),
        success: function(result) {
            if(result.status == 'success')
            {
                let wrapper_tags = $('tr[data-id_item="'+id_item+'"] .wrapper_tags')
                wrapper_tags.removeClass('tag_'+id_tag)
                wrapper_tags.find('.tag_marker[data-id_tag="'+id_tag+'"]').remove()
            }
        },
        error: function(result) {
            error_corpus_not_exists();
        }
    })
}

function handle_click_on_sortable_column(th)
{
    const field = th.prop('class').substring(7);
    const state_sorted = th.data('state_sorted');

    if(state_sorted == 'None')
    {
        th.data('state_sorted', 'asc');
        glob_sorted_columns = [{field: field, order: 'asc'}]; 
    } 
    else if(state_sorted == 'asc')
    {
        th.data('state_sorted', 'desc');
        glob_sorted_columns = [{field: field, order: 'desc'}]; 
    } 
    else 
    {
        th.data('state_sorted', 'None');
        glob_sorted_columns = [];
    }

    refresh_url();
    set_session_entry('viewer__sorted_columns', glob_sorted_columns, function() {
        glob_current_page = 1;
        load_current_page();
        console.log(JSON.stringify(glob_sorted_columns))
    });
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
    $.event.trigger(glob_event_selected_items_update, glob_selected_items);
}

function handle_click_link_add_tag(event, link)
{
    if(glob_mode_add_tag.status == 'inactive')
    {
        event.preventDefault();
        $('#modal_add_tag').data('id_item', link.data('id_item'));
        $('#modal_add_tag').data('viewer__id_item_internal', link.data('viewer__id_item_internal'));
        glob_trigger_modal = 'link';
        $('#modal_add_tag').modal('show')
    }
}
function handle_show_modal(event, modal)
{
    switch(glob_trigger_modal) 
    {
        case undefined:
            // $('#info_count_selected_items').parent().removeClass('text-muted');
            // $('#input_add_to_all_filtered_items').parent().removeClass('text-muted');
            // $('#label_for_input_name_new_tag').removeClass('text-muted');
            let count = 1
            if(modal.data('id_item') == undefined)
            {
                count = Object.keys(glob_selected_items).length
            }
            $('#info_count_selected_items').text(count)
            $('#input_name_new_tag').val('');

            break;
        case 'link':
            // $('#info_count_selected_items').parent().addClass('text-muted');
            // $('#input_add_to_all_filtered_items').parent().addClass('text-muted');
            // $('#label_for_input_name_new_tag').removeClass('text-muted');
            $('#input_name_new_tag').val('');
            break;
        case 'mode_add_tag':
            // $('#info_count_selected_items').parent().css("visibility", "hidden");
            // $('#input_add_to_all_filtered_items').css("visibility", "hidden");
            // $('#label_for_input_name_new_tag').css("visibility", "hidden");

            $('#input_name_new_tag').val($('#input_add_tag').val().trim());
            break;
    }
    // input the count of selected rows into the modal
}

function handle_shown_modal(event, modal)
{
    switch(glob_trigger_modal) 
    {
        case undefined:
            $('#input_name_new_tag').focus();

            break;
        case 'link':
            $('#input_name_new_tag').focus();

            break;
        case 'mode_add_tag':
            $('#input_color_tag').focus();
            break;
    }
    // focus the name field
}

function handle_hide_modal(event, modal)
{
    glob_trigger_modal = undefined;
    // remove the associated data
    modal.removeData('id_item');
}

function export_data(modal)
{
    let data = {}
    data.task = 'export_data'
    data.key_tag = $('#input_name_tag_field').val()
    
    let url_params = refresh_url();

    $.ajax({
        url: glob_current_corpus+'/get_page?'+url_params,
        method: 'POST',
        contentType: 'application/json',
        headers: {'X-CSRFToken':$('input[name="csrfmiddlewaretoken"]').val()},
        data: JSON.stringify(data),
        success: function(result) {
            modal.modal('hide');

        },
        error: function(result) {
            error_corpus_not_exists();
        }
    })
}

function reload_settings()
{
    let data = {}
    data.task = 'reload_settings'
    
    let url_params = refresh_url();

    $.ajax({
        url: glob_current_corpus+'/get_page?'+url_params,
        method: 'POST',
        contentType: 'application/json',
        headers: {'X-CSRFToken':$('input[name="csrfmiddlewaretoken"]').val()},
        data: JSON.stringify(data),
        success: function(result) {
            location.reload();
        },
        error: function(result) {
            error_corpus_not_exists();
        }
    })
}

function reindex_corpus(modal)
{
    let data = {}
    data.task = 'reindex_corpus'
    data.class_handle_index = $('#input_handle_index').val()
    
    let url_params = refresh_url();

    $.ajax({
        url: glob_current_corpus+'/get_page?'+url_params,
        method: 'POST',
        contentType: 'application/json',
        headers: {'X-CSRFToken':$('input[name="csrfmiddlewaretoken"]').val()},
        data: JSON.stringify(data),
        success: function(result) {
        },
        error: function(result) {
            error_corpus_not_exists();
        }
    })
    setTimeout(reload, 1000);
}

function handle_show_modal_reindex_corpus(e, modal)
{
    let data = {}
    data.task = 'get_handle_indices'

    $.ajax({
        method: 'POST',
        contentType: 'application/json',
        headers: {'X-CSRFToken':$('input[name="csrfmiddlewaretoken"]').val()},
        data: JSON.stringify(data),
        success: function(result) {
            let input_select = $('#input_handle_index');
            input_select.html('')
            input_select.append('<option value="">keep current search engine</option>')
            $.each(result.data, function(index, elem) {
                input_select.append('<option value="' + elem.key + '">' + elem.name + '</option>')
                
            })
        },
        error: function(result) {
            error_corpus_not_exists();
        }
    })
    console.log(modal)
}

function delete_corpus(modal)
{
    let data = {}
    data.task = 'delete_corpus'
    data.keep_settings_file = modal.find('input[name="keep_settings_file"]').prop('checked');

    let url_params = refresh_url();

    $.ajax({
        url: glob_current_corpus+'/get_page?'+url_params,
        method: 'POST',
        contentType: 'application/json',
        headers: {'X-CSRFToken':$('input[name="csrfmiddlewaretoken"]').val()},
        data: JSON.stringify(data),
        success: function(result) {
            location.reload();
        },
        error: function(result) {
            error_corpus_not_exists();
        }
    })
}

function submit_token_editing(modal)
{
    let data = {}
    data.task = 'submit_token_editing';
    data.token = $('#input_secret_token').val();

    let url_params = refresh_url();

    $.ajax({
        // url: glob_current_corpus+'/get_page?'+url_params,
        method: 'POST',
        contentType: 'application/json',
        headers: {'X-CSRFToken':$('input[name="csrfmiddlewaretoken"]').val()},
        data: JSON.stringify(data),
        success: function(result) {
            location.reload();
        },
        error: function(result) {
            error_corpus_not_exists();
        }
    })
}

function add_tag(modal)
{
    const id_item = modal.data('id_item');
    const id_item_internal = modal.data('viewer__id_item_internal');
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
            data.ids = []
            $.each(glob_selected_items, function(key, value) {
                data.ids.push(value)
            });
        // if the modal was triggered by a link
        } else {
            data.ids = [{'id_item': id_item, 'viewer__id_item_internal': id_item_internal}]
        }
    }
    // console.log(data);
    // return

    let url_params = refresh_url();
    $.ajax({
        url: glob_current_corpus+'/get_page?'+url_params,
        method: 'POST',
        contentType: 'application/json',
        headers: {'X-CSRFToken':$('input[name="csrfmiddlewaretoken"]').val()},
        data: JSON.stringify(data),
        success: function(result) {
            if(glob_trigger_modal == 'mode_add_tag')
            {
                let button = $('button_start_mode_add_tag');
                button.data('status', 'active');
                button.text('Stop');

                start_mode_add_tag(result.data.tag);
            } else {
                if(data.ids == 'all')
                {
                    $('#table_entities .wrapper_tags').each(function(index, element) {
                        $(element).addClass('tag_'+result.data.tag.id)
                    })
                } else {
                    $.each(data.ids, function(index, value) {
                        $('#table_entities tr[data-id_item="'+value['id_item']+'"] .wrapper_tags').addClass('tag_'+result.data.tag.id)
                    })
                    add_tag_marker(result.data.tag.id, result.data.tag.name, result.data.tag.color)
                }  
            }

            if(result.data.created_tag)
            {
                add_tag_to_tags_list(result.data.tag.id, result.data.tag.name, result.data.tag.color)
            }

            modal.modal('hide');
        },
        error: function(result) {
            error_corpus_not_exists();
        }
    });
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

function handle_click_mode_add_tag(button)
{
    // if add-tag-mode was started
    if(button.data('status') == 'inactive')
    {
        let tag_name = $('#input_add_tag').val().trim();

        if(tag_name == '')
        {
            return;
        }

        let data = {};
        data.task = 'check_if_tag_exists';
        data.name = tag_name;

        $.ajax({
            url: '',
            method: 'POST',
            contentType: 'application/json',
            headers: {'X-CSRFToken':$('input[name="csrfmiddlewaretoken"]').val()},
            data: JSON.stringify(data),
            success: function(result) {
                if(result.data.exists == true)
                {
                    button.data('status', 'active');
                    button.text('Stop');

                    start_mode_add_tag(result.data.tag);
                } else {
                    glob_trigger_modal = 'mode_add_tag';
                    $('#modal_add_tag').modal('show');
                }
            },
            error: function(result) {
                error_corpus_not_exists();
            }
        })

    } else {
        end_mode_add_tag();
    
        button.data('status', 'inactive');
        button.text('Start');
    }
}

function handle_click_on_column_sorted_available(element)
{
    glob_sorted_columns.push({field: $(element).data('id_column'), order: 'asc'});

    update_sorted_columns();
}

function remove_column_sorted_active(div)
{
    glob_sorted_columns.splice(div.index(), 1);

    div.remove();
    
    if($('#wrapper_columns_sorted div').length == 0)
    {
        $('#wrapper_columns_sorted').addClass('d-none');
    }
}

function handle_column_sorted_change_order(div)
{
    const order_active = div.data('order');
    const order_inactive = (order_active == 'desc') ? 'asc': 'desc';

    const index = div.parent().parent().index();
    glob_sorted_columns[index].order = order_active
    
    div.removeClass('badge-secondary').addClass('badge-primary');
    div.parent().find('[data-order="'+order_inactive+'"]').removeClass('badge-primary').addClass('badge-secondary');
}

function handle_column_sorted_move(badge)
{
    const direction = badge.data('direction');
    const row = badge.parent().parent();

    // console.log(glob_sorted_columns)

    const index_current = row.index();
    const index_new = (direction == 'up') ? index_current - 1 : index_current + 1;
    console.log(index_new);

    const removedElement = glob_sorted_columns.splice(index_current, 1)[0]

    glob_sorted_columns.splice(index_new, 0, removedElement);

    console.log(glob_sorted_columns)
    update_sorted_columns();

    // index = this.indexOf(element)
    // newIndex = index + offset

    // if newIndex > -1 && newIndex < this.length
    //     # Remove the element from the array
    //     removedElement = this.splice(index, 1)[0]

    // # At "newIndex", remove 0 elements, insert the removed element
    // this.splice(newIndex, 0, removedElement)
}

function handle_column_sorted_apply()
{
    refresh_url();
    set_session_entry('viewer__sorted_columns', glob_sorted_columns, function() {
        glob_current_page = 1;
        load_current_page();
    });
}

function handle_click_on_tr(event, tr)
{
    if(glob_mode_add_tag.status == 'active')
    {
        let tag  = glob_mode_add_tag.tag;
        let id_item = tr.data('id_item')
        let id_item_internal = tr.data('viewer__id_item_internal')
        let data = {}
        data.task = 'toggle_item_to_tag'
        data.id_tag = tag.id;
        data.id_item = id_item;
        data.viewer__id_item_internal = id_item_internal;

        $.ajax({
            url: '',
            method: 'POST',
            contentType: 'application/json',
            headers: {'X-CSRFToken':$('input[name="csrfmiddlewaretoken"]').val()},
            data: JSON.stringify(data),
            success: function(result) {
                if(result.data.removed == true)
                {
                    $('#table_entities tr[data-id_item="'+id_item+'"] .wrapper_tags').removeClass('tag_'+tag.id)
                    remove_tag_marker(tag.id, id_item);
                } else {
                    $('#table_entities tr[data-id_item="'+id_item+'"] .wrapper_tags').addClass('tag_'+tag.id)
                    add_tag_marker(tag.id, tag.name, tag.color)
                }
            },
            error: function(result) {
                error_corpus_not_exists();
            }
        })
    }
}

function handle_change_displayed_tag_all(input)
{
    if(input.prop('checked'))
    {
        $('.checkbox_tag_selection').each(function(index, element) {
            let checkbox = $(element)
            let id_tag = checkbox.data('id_tag');
            let tag_name = checkbox.data('tag_name');
            let tag_color = checkbox.data('tag_color');
            glob_selected_tags[id_tag] = id_tag;
            add_tag_marker(id_tag, tag_name, tag_color);
            checkbox.prop('checked', true)
        })
    } else {
        $('.checkbox_tag_selection').each(function(index, element) {
            let checkbox = $(element)
            let id_tag = checkbox.data('id_tag');
            delete glob_selected_tags[id_tag];
            // set_session_entry('viewer__selected_tags', glob_selected_tags)
            remove_tag_marker(id_tag);
            checkbox.prop('checked', false)
        })
    }
    set_session_entry('viewer__selected_tags', glob_selected_tags);
}

function handle_change_displayed_tag(checkbox)
{
    let id_tag = checkbox.data('id_tag');
    let tag_name = checkbox.data('tag_name');
    let tag_color = checkbox.data('tag_color');
    if(checkbox.prop('checked'))
    {
        glob_selected_tags[id_tag] = id_tag;
        set_session_entry('viewer__selected_tags', glob_selected_tags)
        add_tag_marker(id_tag, tag_name, tag_color);
    } else {
        delete glob_selected_tags[id_tag];
        set_session_entry('viewer__selected_tags', glob_selected_tags)
        remove_tag_marker(id_tag);
    }
    update_checkbox_select_all('checkbox_tag_selection', 'checkbox_tag_selection_all')
}

function load_current_page(update_tags = true)
{
    let url_params = refresh_url();

    $.ajax({
        url: glob_current_corpus+'/get_page?'+url_params,
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
                    add_tag_marker($(element).data('id_tag'), $(element).data('tag_name'), $(element).data('tag_color'));
                });
            }

            update_ui(result.info_filter_values);
            stop_loading();
        },
        error: function(result) {
            error_corpus_not_exists();
        }
    });
}

function load_page_parameters()
{
    glob_current_corpus = $('input[name=id_corpus]').val();

    $.each($('#json_url_params').data('json_url_params'), function(key, value){
        if(key.startsWith('viewer__'))
        {
            if(key == 'viewer__page')
            {
                glob_current_page = parseInt(value)
            } else if(key == 'viewer__columns') {
                glob_columns = value
            } else if(key == 'viewer__sorted_columns') {
                glob_sorted_columns = value
            } else if(key == 'viewer__filter_tags') {
                glob_filter_tags = value
            } else if(key == 'viewer__filter_custom') {
                glob_filter_custom = value
            }
        }
    })

    $.each($('#tag_filter_active').data('tag_filter_active'), function(key, value){
        glob_dict_filter_tags[key] = value;
    });
}

// function load_filters()
// {
//     $.each($('#json_filters').data('json_filters'), function(key, value){
//         $(document).on(value.event, '#input_'+value.data_field, function(){
//             let data_field = $(this).prop('name')
//             let value = $(this).val()
//             glob_filter_custom[data_field] = value

//             set_session_entry('viewer__filter_custom', glob_filter_custom, function() {
//                 glob_current_page = 1;
//                 load_current_page();
//             })
//         });
//     })
// }
