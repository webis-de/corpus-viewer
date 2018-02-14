let glob_selected_items = {}
const glob_event_selected_items_update = jQuery.Event('update.cv.selected-items');

let glob_selected_tags = {}

let glob_filter_tags = []
let glob_dict_filter_tags = {}
let glob_filter_custom = {}
let glob_sorted_columns = []
let glob_columns = []

let glob_current_page = 1;
let glob_current_corpus = '';
let glob_prev_page = undefined;
let glob_next_page = undefined;
let glob_count_pages = undefined;
let glob_count_entries = undefined;

let glob_mode_add_tag = {status: 'inactive', tag: {id: '', name: '', color: ''}};
let glob_trigger_modal = undefined;

let glob_template_filter_active_contains = `
    <div data-value="PLACEHOLDER_VALUE" class="pl-1 pr-1">
        <span>PLACEHOLDER_VALUE_REAL</span>
        <span class="float-right">
            PLACEHOLDER_TEMPLATE_CASE_SENSITIVITY
            <span class="fa fa-info" data-toggle="popover" data-content="PLACEHOLDER_TEMPLATE_INFO_FILTER_VALUES"></span>
            <span class="fa fa-times" data-value="PLACEHOLDER_VALUE" data-data_field="PLACEHOLDER_DATA_FIELD"></span>
        </span>
    </div>`;

let glob_template_filter_active_number = `
    <div data-value="PLACEHOLDER_VALUE" class="pl-1 pr-1">
        <span>PLACEHOLDER_VALUE</span>
        <span class="float-right">
            <span class="fa fa-info" data-toggle="popover" data-content="PLACEHOLDER_TEMPLATE_INFO_FILTER_VALUES"></span>
            <span class="fa fa-times" data-value="PLACEHOLDER_VALUE" data-data_field="PLACEHOLDER_DATA_FIELD"></span>
        </span>
    </div>`;

let glob_template_filter_active_tag = `
    <div data-value="PLACEHOLDER_VALUE" class="pl-1 pr-1 filter_active_tag">
        <div data-type="color" class="d-inline-block" style="background-color: PLACEHOLDER_COLOR"></div>
        <span>PLACEHOLDER_VALUE</span>
        <span class="float-right">
            <span class="fa fa-times" data-value="PLACEHOLDER_VALUE"></span>
        </span>
    </div>`;

let glob_template_info_filter_values_contains = escape_html(`
    <table class="table table-bordered table-sm">
        <tr>
            <td>term frequency</td>
            <td>PLACEHOLDER_VALUE_COUNT_TOTAL</td>
        </tr>
        <tr>
            <td>document frequency</td>
            <td>PLACEHOLDER_VALUE_COUNT_PER_DOCUMENT</td>
        </tr>
    </table>`);

let glob_template_info_filter_values_number = escape_html(`
    <table class="table table-bordered table-sm">
        <tr>
            <td>document frequency</td>
            <td>PLACEHOLDER_VALUE_COUNT_PER_DOCUMENT</td>
        </tr>
    </table>`);

let glob_template_sorted_column_active = `
    <div data-id_column="PLACEHOLDER_ID_COLUMN" class="sorted_column_active p-1">
        <span>PLACEHOLDER_COLUMN</span>
        <span class="float-right">
            <span data-order="asc" class="badge PLACEHOLDER_ASC" style="cursor: pointer">asc</span>
            <span data-order="desc" class="badge PLACEHOLDER_DESC" style="cursor: pointer">desc</span>

            <span data-direction="up" class="badge btn-secondary" style="cursor: pointer">
                <i class="fa fa-long-arrow-up"></i>
            </span>
            <span data-direction="down" class="badge btn-secondary" style="cursor: pointer">
                <i class="fa fa-long-arrow-down"></i>
            </span>
            
            <i class="fa fa-times text-danger" style="cursor: pointer"></i>
        </span>
    </div>`;

$(document).ready(function()
{
    $(document).on('click', '#share_link', function(event) {
        const elem_input = $('#input_share_link');
        elem_input.text(window.location.href);
        elem_input[0].select();
        const successful = document.execCommand('copy');
        if(successful)
        {
            $('#share_link').popover('show');
            setTimeout(function() {
                $('#share_link').popover('hide');
            } ,700)
        }
    })

    function trigger_tag_new_change(recommendation, input)
    {
        let tag = {
            id: recommendation.data('tag_id'),
            name: recommendation.data('tag_name'),
            color: recommendation.data('tag_color')
        }

        input.val(tag.name);
        console.log(tag)
        $('#input_color_tag').val(tag.color);
    }

    function trigger_tag_add_change(recommendation, input)
    {
        let tag = {
            id: recommendation.data('tag_id'),
            name: recommendation.data('tag_name'),
            color: recommendation.data('tag_color')
        }
        console.log(tag)

        input.val(tag.name);
        $('#button_start_mode_add_tag').data('tag', tag);
    }

    function trigger_tag_filter_change(recommendation, input)
    {
        let tag = {
            id: recommendation.data('tag_id'),
            name: recommendation.data('tag_name'),
            color: recommendation.data('tag_color')
        }

        input.val('');

        glob_filter_tags.push(tag.name);
        glob_dict_filter_tags[tag.name] = tag;
        set_session_entry('viewer__filter_tags', glob_filter_tags, function() {
            glob_current_page = 1;
            load_current_page();
        })
    }

    let recommendation_tag_filter = new Recommendation(document, '#input_filter_tags', '#wrapper_tag_recommendations_filter', trigger_tag_filter_change);
    let recommendation_tag_new = new Recommendation(document, '#input_name_new_tag', '#wrapper_tag_recommendations_new', trigger_tag_new_change);
    let recommendation_tag_assign = new Recommendation(document, '#input_add_tag', '#wrapper_tag_recommendations_add_tag', trigger_tag_add_change);

    kritten_resize_manager.set_callback_mouseup(function(row_is_hidden, width_current) {
        if(row_is_hidden)
        {
            set_session_entry('width_filters', false);
        } else {
            set_session_entry('width_filters', width_current);
        }
    });

    kritten_resize_manager.set_callback_click(function(width_last) {
        set_session_entry('width_filters', width_last);
    });

    $(document).on('change', '#input_page', function() { handle_page_input($(this)) });
    $(document).on('click', '#info_paginator button', function(e) { e.preventDefault(); handle_pager_click($(this)) });

    $(document).on('click', '#wrapper_tag_filter_active .fa-times', function(){handle_remove_tag_from_filter($(this))});

    $(document).on('click', '.viewer__button_case_sensitivity', function(){ handle_click_on_button_case_sensitivity($(this)) });
    $(document).on('click', '.viewer__button_add_filter_contains', function(){ handle_click_on_button_add_filter_contains($(this)) });
    $(document).on('click', '.viewer__button_add_filter_number', function(){ handle_click_on_button_add_filter_number($(this)) });
    $(document).on('click', '.viewer__button_boolean', function(){ handle_click_on_button_boolean($(this)) });
    $(document).on('click', '.viewer__column_filter_active .fa-times', function(){ handle_click_on_remove_filter_value($(this)) });

    // $('.viewer__column_filter_active .fa-info').popover({
    //     selector: '.viewer__column_filter_active .fa-info',
    //     placement: 'top',
    //     animation: false,
    //     container: 'body',
    //     html: true,
    //     trigger: 'hover',
    //     // template: '<div class="popover link_delete_tag" style="cursor:pointer" role="tooltip"><div class="popover-content" style="padding: 3px 5px"></div></div>'
    // })


    $(document).on('update.cv.selected-items', function(e) { console.log('update.cv.selected-items') });


    $(document).on('show.bs.collapse', '.card .collapse', function(e) { set_session_entry('is_collapsed_'+$(this).attr('id'), false) });
    $(document).on('hide.bs.collapse', '.card .collapse', function(e) { set_session_entry('is_collapsed_'+$(this).attr('id'), true) });

    $(document).on('click', '#link_reset_filters', function(e) { handle_reset_filters($(this)) });

    $(document).on('change', '#input_toggle_columns_all', function(e) { handle_toggle_column_all($(this)) });
    $(document).on('change', '.input_toggle_columns', function(e) { handle_toggle_column($(this)) });

    $(document).on('change', '#input_select_all_items', function(e) { handle_selection_all_items($(this)) });
    $(document).on('change', '.input_select_item', function(e) { handle_select_item($(this), e) });
    $(document).on('click', '#button_select_all_items', function(e) { handle_click_on_button_select_all_items($(this)) });
    $(document).on('click', '#button_deselect_all_items', function(e) { handle_click_on_button_deselect_all_items($(this)) });

    $(document).on('click', '.viewer__column_type_text .fixed_table', function(e) { handle_toggle_container_text($(this)) });
    $(document).on('mouseover', '.viewer__column_type_text .fixed_table', function(e) { handle_mouseover_popover_text($(this)) });
    $(document).on('mouseout', '.viewer__column_type_text .fixed_table', function(e) { handle_mouseout_popover_text($(this)) });
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
    $(document).on('click', '#toggle_popover_add_column_sorted', function(e) { return false });
    // hide popovers on click anywhere
    $(document).on('click', 'body', function(e) { $('.tag_marker').popover('hide'); $('#toggle_popover_add_column_sorted').popover('hide') });
    $(document).on('show.bs.popover', '.tag_marker', function(e) { $('.tag_marker').popover('hide') });

    $(document).tooltip({
        selector: '.tag_marker',
        placement: 'top',
        animation: false,
        container: 'body',
    });

    $('body').tooltip({
        selector: '.tooltip_name_tag',
        placement: 'top',
        animation: false,
        container: 'body',
    });

    $('body').popover({
        selector: '.tag_marker',
        placement: 'bottom',
        animation: false,
        container: 'body',
        html: true,
        template: '<div class="popover link_delete_tag" style="cursor:pointer" role="tooltip"><div class="popover-body" style="padding: 3px 5px"></div></div>'
    });

    //////////////////////

    $(document).popover({
        selector: '#toggle_popover_add_column_sorted',
        placement: 'right',
        animation: false,
        container: 'body',
        html: true,
        content: function() {
            let result = '';
            let list_columns_used = [];

            $('#wrapper_columns_sorted div').each(function(index, div) {
                list_columns_used.push($(div).data('id_column'));
            });

            $(glob_columns).each(function(index, column) {
                if(list_columns_used.indexOf(column) == -1 && column != 'viewer__tags' && column != 'viewer__item_selection' && column != 'viewer__view_item')
                {
                    result += '<div class="column_sorted_available" data-id_column="'+column+'" style="cursor:pointer">'+column+'</div>';
                }
            });

            return result;
        },
        template: '<div class="popover popover_column_sorted_available" role="tooltip"><div class="popover-body" style="padding: 3px 5px"></div></div>'
    });
    $(document).on('click', '.column_sorted_available', function(e) { handle_click_on_column_sorted_available($(this)) });
    $(document).on('click', '.sorted_column_active .fa-times', function(e) { remove_column_sorted_active($(this).parent().parent()) });
    $(document).on('click', '.sorted_column_active [data-order]', function(e) { handle_column_sorted_change_order($(this)) });
    $(document).on('click', '.sorted_column_active [data-direction]', function(e) { handle_column_sorted_move($(this)) });
    $(document).on('click', '#toggle_popover_apply_column_sorted', function(e) { handle_column_sorted_apply($(this)) });

    $(document).on('click', 'th[data-sortable="sortable"]', function(e) {handle_click_on_sortable_column($(this)) });
    //////////////////////

    $(document).on('contextmenu', '.row_viewer__item', function(e) {handle_rightclick_on_tr(e, $(this))})

    $(document).on('click', '.link_add_tag', function(e) { handle_click_link_add_tag(e, $(this)) });
    $(document).on('show.bs.modal', '#modal_add_tag', function(e) { handle_show_modal(e, $(this)) });
    $(document).on('shown.bs.modal', '#modal_add_tag', function(e) { handle_shown_modal(e, $(this)) });
    $(document).on('hide.bs.modal', '#modal_add_tag', function(e) { handle_hide_modal(e, $(this)) });
    $(document).on('click', '#submit_add_tag', function(e) { add_tag($('#modal_add_tag')) });
    $(document).on('change', '#input_add_to_all_filtered_items', function(e) { handle_change_add_to_all_filtered_items($(this)) });

    $(document).on('click', '#button_start_mode_add_tag', function(){ handle_click_mode_add_tag($(this)) });
    $(document).on('click', '.row_viewer__item', function(e) {handle_click_on_tr(e, $(this))})

    
    $(document).on('click', '#submit_export_data', function(e) { export_data($('#modal_export_data')) });
    $(document).on('click', '#submit_reload_settings', function(e) { reload_settings() });
    $(document).on('click', '#submit_reindex_corpus', function(e) { reindex_corpus($('#modal_reindex_corpus')) });
    $(document).on('show.bs.modal', '#modal_reindex_corpus', function(e) { handle_show_modal_reindex_corpus(e, $(this)) });
    $(document).on('click', '#submit_delete_corpus', function(e) { delete_corpus($('#modal_delete_corpus')) });
    $(document).on('click', '#submit_enter_token_editing', function(e) { submit_token_editing($('#modal_enter_token_editing')) });

    $(document).on('change', '#checkbox_tag_selection_all', function(e) { handle_change_displayed_tag_all($(this)) });
    $(document).on('change', '.checkbox_tag_selection', function(e) { handle_change_displayed_tag($(this)) });

    load_page_parameters()
    load_current_page();
});