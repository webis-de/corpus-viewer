let glob_columns = []

let glob_current_page = 1;
let glob_prev_page = undefined;
let glob_next_page = undefined;
let glob_count_pages = undefined;
let glob_count_entries = undefined;

$(document).ready(function()
{
    load_page_parameters()

    $(document).on('change', '#input_page', function() { handle_page_input($(this)) });
    $(document).on('click', '#info_paginator button', function(e) { e.preventDefault(); handle_pager_click($(this)) });
	
	$(document).on('show.bs.collapse', '.card .collapse', function() { set_session_entry('is_collapsed_'+$(this).attr('id'), false) });
	$(document).on('hide.bs.collapse', '.card .collapse', function() { set_session_entry('is_collapsed_'+$(this).attr('id'), true) });

    $(document).on('change', '.input_toggle_columns', function(e) { handle_toggle_column($(this)) });

    load_current_page();
});