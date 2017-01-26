let glob_selected_items = {}

let glob_columns = []

let glob_current_page = 1;
let glob_prev_page = undefined;
let glob_next_page = undefined;
let glob_count_pages = undefined;
let glob_count_entries = undefined;

$(document).ready(function()
{
    $(document).on('change', '#input_page', function() { handle_page_input($(this)) });
    $(document).on('click', '#info_paginator button', function(e) { e.preventDefault(); handle_pager_click($(this)) });
    
    $(document).on('show.bs.collapse', '.card .collapse', function(e) { set_session_entry('is_collapsed_'+$(this).attr('id'), false) });
    $(document).on('hide.bs.collapse', '.card .collapse', function(e) { set_session_entry('is_collapsed_'+$(this).attr('id'), true) });

    $(document).on('change', '.input_toggle_columns', function(e) { handle_toggle_column($(this)) });

    $(document).on('change', '#input_select_all_items', function(e) { handle_selection_all_items($(this)) });
    $(document).on('change', '.input_select_item', function(e) { handle_select_item($(this)) });
    $(document).on('click', '#link_deselect_all_items', function(e) { handle_deselect_all_items(e) });
    // $(document).on('contextmenu', '.row_viewer__item', function(e) {handle_rightclick_on_tr(e, $(this))})

    $(document).on('click', '.link_add_tag', function(e) { handle_click_link_add_tag(e, $(this)) });
    $(document).on('show.bs.modal', '#modal_add_tag', function(e) { handle_show_modal(e, $(this)) });
    $(document).on('shown.bs.modal', '#modal_add_tag', function(e) { handle_shown_modal(e, $(this)) });
    $(document).on('hide.bs.modal', '#modal_add_tag', function(e) { handle_hide_modal(e, $(this)) });
    $(document).on('click', '#submit_add_tag', function(e) { add_tag($('#modal_add_tag')) });
    $(document).on('change', '#input_add_to_all_filtered_items', function(e) { handle_change_add_to_all_filtered_items($(this)) });

    $(document).on('change', '#checkbox_tag_selection_all', function(e) { handle_change_displayed_tag_all($(this)) });
    $(document).on('change', '.checkbox_tag_selection', function(e) { handle_change_displayed_tag($(this)) });

    load_page_parameters()

    load_current_page();
});