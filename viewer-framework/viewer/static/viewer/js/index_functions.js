function load_current_page(update_tags = true)
{
    // refresh_url();

    $.ajax({
        url: 'get_page',
        beforeSend: function() {
            $('#table_entities .wrapper_loading').show();
        },
        success: function(result) {
            console.log()
            $('#table_entities .content').html(result)
        //     glob_prev_page = result.previous_page_number;
        //     glob_next_page = result.next_page_number;
        //     glob_count_pages = result.count_pages;
        //     glob_count_entries = result.count_entries

        //     // if(update_tags)
        //     // {
        //     //     update_tags_list(result.tags);
        //     // } else {
        //     //     $.each($('.checkbox_tag_selection:checked'), function(index, element) {
        //     //         add_tag_marker($(element).data('tag_id'), $(element).data('tag_name'), $(element).data('tag_color'));
        //     //     });
        //     // }

        //     update_ui();
            $('#table_entities .wrapper_loading').hide();
        },
    });
}
// important
function refresh_url()
{
    var data = {};
    data.current_page = glob_cur_page;

    data.sort_by = glob_sort_by;
    data.order = glob_order;

    data.filter_tag = JSON.stringify(glob_filter_tag);
    data.filter_twitter_users = JSON.stringify(glob_filter_twitter_users)
    data.filter_start_datetime = glob_filter_start_datetime
    data.filter_end_datetime = glob_filter_end_datetime
    data.filter_text_content = glob_filter_text_content

    var url_params = '';
    $.each(data, function(index, value) {
        url_params += index+'='+value+'&';
    });
    url_params += 'time='+Date.now();
    // TODO: pushState?
    // history.pushState(null, null, '?'+url_params);
    history.replaceState(null, null, '?'+url_params);
}