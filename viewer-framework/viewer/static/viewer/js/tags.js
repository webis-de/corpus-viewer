let glob_clicked_enter = false;

$(document).ready(function()
{
    $(document).on('click', '.column_tag_name[data-original_value]', function() { make_text_input($(this)) });
    $(document).on('blur', '.column_tag_name[data-original_value] input', function() { if(!glob_clicked_enter) {save_new_name($(this));} glob_clicked_enter = false  });
    $(document).on('keyup', '.column_tag_name[data-original_value] input', function(e) { if (e.keyCode == 13) {glob_clicked_enter = true; save_new_name($(this))} });

    $(document).on('hide.bs.modal', '#modal_merge_tags', function() { revert_input_field($('tr[data-id_tag="'+$('#modal_merge_tags').data('id_tag')+'"] .column_tag_name[data-original_value] input')); });

    $(document).on('change', '.column_tag_color input', function() { save_new_color($(this)) });

    $(document).on('click', '.column_delete_tag i', function() { request_delete_tag($(this).parent().parent().data('id_tag'), $(this).parent().parent().data('tag_name')) });
    
    $(document).on('show.bs.modal', '#modal_add_items', function(event) { add_id_tag_to_modal($(event.relatedTarget)) });
    $(document).on('click', '#submit_add_items', function() { add_items($('#modal_add_items')); });
});

function add_id_tag_to_modal(button)
{
    let id_tag = button.parent().parent().data('id_tag');
    $('#modal_add_items').data('id_tag', id_tag);
}

function add_items(modal)
{
    let data = {}
    data.task = 'add_items';
    data.id_tag = modal.data('id_tag');
    data.ids = $('#input_list_items').val();

    $.ajax({
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
    });
}

function export_tags(modal)
{
    let url = 'tags/export';

    // const list_ids = [];
    // $.each(glob_selected_items, function( i, val ) {
    //     list_ids.push(val.viewer__id_item_internal);
    // });
    // url += JSON.stringify(list_ids);
    window.open(url, '_blank');
    modal.modal('hide');

    // let data = {};
    // data.task = 'export_tags';
    // data.path = $('#'+modal.attr('id')+' input[name="path"]').val();

    // $.ajax({
    //     method: 'POST',
    //     contentType: 'application/json',
    //     headers: {'X-CSRFToken':$('input[name="csrfmiddlewaretoken"]').val()},
    //     data: JSON.stringify(data),
    //     success: function(result) {
    //         modal.modal('hide');
    //     },
    // });
}

function import_tags(modal)
{
    let data_form = new FormData();
    data_form.append('csrfmiddlewaretoken', $('input[name="csrfmiddlewaretoken"]').val());
    data_form.append('file', modal.find('input[type="file"]')[0].files[0]);

    // let data = {};
    // data.task = 'import_tags';
    // data.path = data_form;
    // data.path = data_form;

    $.ajax({
        method: 'POST',
        // contentType: 'application/json',
        headers: {'X-CSRFToken':$('input[name="csrfmiddlewaretoken"]').val()},
        contentType: false,
        data: data_form,
        processData: false,
        success: function(result) {
            location.reload();
        },
    });
    return
    // let data = {};
    // data.task = 'import_tags';
    // data.path = $('#'+modal.attr('id')+' input[name="path"]').val();

    // $.ajax({
    //     method: 'POST',
    //     contentType: 'application/json',
    //     headers: {'X-CSRFToken':$('input[name="csrfmiddlewaretoken"]').val()},
    //     data: JSON.stringify(data),
    //     success: function(result) {
    //         modal.modal('hide');
    //     },
    // });
}

function request_delete_tag(id_tag, tag_name)
{
    $('#modal_delete_tag .modal-body span:nth-of-type(1)').text(tag_name);

    $('#modal_delete_tag').data('id_tag', id_tag);

    $('#modal_delete_tag').modal('show');
}

function delete_tag(modal)
{
    let data = {};
    data.task = 'delete_tag';
    data.id_tag = modal.data('id_tag');;

    $.ajax({
        method: 'POST',
        contentType: 'application/json',
        headers: {'X-CSRFToken':$('input[name="csrfmiddlewaretoken"]').val()},
        data: JSON.stringify(data),
        success: function(result) {
            $('tr[data-id_tag="'+data.id_tag+'"]').remove();
            modal.modal('hide');
        },
    });
}

function save_new_color(input)
{
    let td = input.parent();
    let new_color = input.val();

    if(new_color == td.data('original_value'))
    {
        return;
    }

    let data = {};
    data.task = 'update_color';
    data.id_tag = td.parent().data('id_tag');
    data.new_color = new_color;

    $.ajax({
        method: 'POST',
        contentType: 'application/json',
        headers: {'X-CSRFToken':$('input[name="csrfmiddlewaretoken"]').val()},
        data: JSON.stringify(data),
        success: function(result) {
            td.data('original_value', new_color);
        },
    });
}

function merge_tags(modal)
{
    let data = {};
    data.task = 'merge_tags';
    data.id_tag = modal.data('id_tag');
    data.existing_tag = modal.data('existing_tag');

    $.ajax({
        method: 'POST',
        contentType: 'application/json',
        headers: {'X-CSRFToken':$('input[name="csrfmiddlewaretoken"]').val()},
        data: JSON.stringify(data),
        success: function(result) {
            $('tr[data-id_tag="'+data.existing_tag+'"] .column_tag_count_items').text(result.data.count_entities_updated)
            $('tr[data-id_tag="'+data.id_tag+'"]').remove();
            modal.modal('hide');
        },
    });
}

function save_new_name(input)
{
    let td = input.parent();
    let new_name = input.val().trim();

    if(new_name == td.data('original_value'))
    {
        console.log('same name')
        remove_input_field(input);
        return;
    }

    let data = {};
    data.task = 'update_name';
    data.id_tag = td.parent().data('id_tag');
    data.new_name = new_name;

    $.ajax({
        method: 'POST',
        contentType: 'application/json',
        headers: {'X-CSRFToken':$('input[name="csrfmiddlewaretoken"]').val()},
        data: JSON.stringify(data),
        success: function(result) {
            if(result.status == 'success')
            {
                console.log('saved new name')
                remove_input_field(input);
            } else {
                $('#modal_merge_tags .modal-body p:nth-of-type(1) span:nth-of-type(1)').text(result.data.existing_tag_name);
                $('#modal_merge_tags .modal-body p:nth-of-type(2) span:nth-of-type(1)').text(result.data.id_tag_name);
                $('#modal_merge_tags .modal-body p:nth-of-type(2) span:nth-of-type(2)').text(result.data.existing_tag_name);

                $('#modal_merge_tags').data('id_tag', result.data.id_tag);
                $('#modal_merge_tags').data('existing_tag', result.data.existing_tag);

                $('#modal_merge_tags').modal('show');
            }
        },
    });
}

function revert_input_field(input)
{
    let td = input.parent();
    td.html(td.data('original_value'));
}

function remove_input_field(input)
{
    let td = input.parent();
    let new_name = input.val().trim().replace(/ /g, '-');
    td.data('original_value', new_name);
    td.html(new_name);
}

function make_text_input(column)
{
    if(column.find('input').length == 0)
    {
        let current_name = column.text().trim();
        column.html('<input style="height: 1.5rem" type="text" value="'+current_name+'">');
        column.find('input').select();
    }
}