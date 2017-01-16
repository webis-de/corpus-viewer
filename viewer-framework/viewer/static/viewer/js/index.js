var glob_current_page = 1;
var glob_prev_page = undefined;
var glob_next_page = undefined;
var glob_count_pages = undefined;
var glob_count_entries = undefined;

$(document).ready(function()
{
    load_page_parameters()

    $(document).on('change', '#input_page', function() { handle_page_input($(this)) });
    $(document).on('click', '#info_paginator button', function(e) { e.preventDefault(); handle_pager_click($(this)) });

    load_current_page();
});