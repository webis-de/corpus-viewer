let glob_selected_items = {}
let glob_selected_tags = {}

let glob_filter_tags = []
let glob_filter_custom = {}
let glob_columns = []

let glob_current_page = 1;
let glob_current_corpus = '';
let glob_prev_page = undefined;
let glob_next_page = undefined;
let glob_count_pages = undefined;
let glob_count_entries = undefined;

let glob_mode_add_tag = {status: 'inactive', tag: {id: '', name: '', color: ''}};

$(document).ready(function()
{
    $(document).on('change', '#input_page', function() { handle_page_input($(this)) });
    $(document).on('click', '#info_paginator button', function(e) { e.preventDefault(); handle_pager_click($(this)) });

    $(document).on('click', '#list_filter_tags .badge .fa-times', function(){handle_remove_tag_from_filter($(this).parent().text().trim())});
    $(document).on('input', '#input_filter_tags', function(){handle_recommendation_filter($(this), $('#wrapper_tag_recommendations_filter'))});
    $(document).on('click', '#wrapper_tag_recommendations_filter .recommendation', function(){handle_click_on_recommendation_filter($(this), trigger_tag_filter_change)});


    $(document).on('show.bs.collapse', '.card .collapse', function(e) { set_session_entry('is_collapsed_'+$(this).attr('id'), false) });
    $(document).on('hide.bs.collapse', '.card .collapse', function(e) { set_session_entry('is_collapsed_'+$(this).attr('id'), true) });

    $(document).on('click', '#link_reset_filters', function(e) { handle_reset_filters($(this)) });

    $(document).on('change', '#input_toggle_columns_all', function(e) { handle_toggle_column_all($(this)) });
    $(document).on('change', '.input_toggle_columns', function(e) { handle_toggle_column($(this)) });

    $(document).on('change', '#input_select_all_items', function(e) { handle_selection_all_items($(this)) });
    $(document).on('change', '.input_select_item', function(e) { handle_select_item($(this)) });
    $(document).on('click', '#link_deselect_all_items', function(e) { handle_deselect_all_items(e) });

    //
    // popover-handling for tag-deletion
    //
    // write id of item into popover-link
    $(document).on('shown.bs.popover', '.wrapper_tags .tag_marker', function(e) {
        $('.link_delete_tag').data('id_item', $(this).parent().parent().parent().data('id_item'))
        $('.link_delete_tag').data('id_tag', $('.link_delete_tag .fa').data('id_tag'))
    });
    // trigger tag-deletion
    $(document).on('click', '.link_delete_tag', function(e) { delete_tag_from_item($(this).data('id_item'), $(this).data('id_tag')); });
    // stop propagation of click event
    $(document).on('click', '.wrapper_tags .tag_marker', function(e) { return false });
    // hide popovers on click anywhere
    $(document).on('click', 'body', function(e) { $('.tag_marker').popover('hide') });
    $(document).on('show.bs.popover', '.tag_marker', function(e) { $('.tag_marker').popover('hide') });

    $('body').tooltip({
        selector: '.tag_marker',
        placement: 'top',
        animation: false,
        container: 'body',
    })
    $('body').popover({
        selector: '.tag_marker',
        placement: 'bottom',
        animation: false,
        container: 'body',
        html: true,
        template: '<div class="popover link_delete_tag" style="cursor:pointer" role="tooltip"><div class="popover-content" style="padding: 3px 5px"></div></div>'
    })

    $(document).on('contextmenu', '.row_viewer__item', function(e) {handle_rightclick_on_tr(e, $(this))})

    $(document).on('click', '.link_add_tag', function(e) { handle_click_link_add_tag(e, $(this)) });
    $(document).on('show.bs.modal', '#modal_add_tag', function(e) { handle_show_modal(e, $(this)) });
    $(document).on('shown.bs.modal', '#modal_add_tag', function(e) { handle_shown_modal(e, $(this)) });
    $(document).on('hide.bs.modal', '#modal_add_tag', function(e) { handle_hide_modal(e, $(this)) });
    $(document).on('click', '#submit_add_tag', function(e) { add_tag($('#modal_add_tag')) });
    $(document).on('change', '#input_add_to_all_filtered_items', function(e) { handle_change_add_to_all_filtered_items($(this)) });

    $(document).on('input', '#input_add_tag', function(){handle_recommendation_filter($(this), $('#wrapper_tag_recommendations_add_tag'))});
    $(document).on('click', '#wrapper_tag_recommendations_add_tag .recommendation', function(){handle_click_on_recommendation_filter($(this), trigger_tag_add_change)});
    $(document).on('click', '#button_start_mode_add_tag', function(){ handle_click_mode_add_tag($(this)) });
    $(document).on('click', '.row_viewer__item', function(e) {handle_click_on_tr(e, $(this))})

    
    $(document).on('click', '#submit_export_data', function(e) { export_data($('#modal_export_data')) });

    $(document).on('change', '#checkbox_tag_selection_all', function(e) { handle_change_displayed_tag_all($(this)) });
    $(document).on('change', '.checkbox_tag_selection', function(e) { handle_change_displayed_tag($(this)) });

    load_page_parameters()

    // FILTERS
    load_filters()
    load_current_page();
});