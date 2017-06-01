$(document).ready(function()
{
    $(document).on('click', '.card', function() { 
        let key = $(this).data('key');
        window.location.href = 'viewer?viewer__current_corpus='+key;
        // let data = {};
        // data.task = 'set_current_corpus';
        // data.corpus = key;

        // $.ajax({
        //     url: '',
        //     method: 'POST',
        //     contentType: 'application/json',
        //     headers: {'X-CSRFToken':$('input[name="csrfmiddlewaretoken"]').val()},
        //     data: JSON.stringify(data),
        //     success: function(result) {
        //     }
        // })
    });
});