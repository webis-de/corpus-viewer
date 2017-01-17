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

        //     // if(update_tags)
        //     // {
        //     //     update_tags_list(result.tags);
        //     // } else {
        //     //     $.each($('.checkbox_tag_selection:checked'), function(index, element) {
        //     //         add_tag_marker($(element).data('tag_id'), $(element).data('tag_name'), $(element).data('tag_color'));
        //     //     });
        //     // }

            update_ui();
            stop_loading();
        },
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
    // data.viewer__columns = glob_columns;
    data.viewer__columns = JSON.stringify(glob_columns);

    // data.sort_by = glob_sort_by;
    // data.order = glob_order;

    // data.filter_tag = JSON.stringify(glob_filter_tag);
    // data.filter_twitter_users = JSON.stringify(glob_filter_twitter_users)
    // data.filter_start_datetime = glob_filter_start_datetime
    // data.filter_end_datetime = glob_filter_end_datetime
    // data.filter_text_content = glob_filter_text_content

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