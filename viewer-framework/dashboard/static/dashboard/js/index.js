$(document).ready(function()
{
    $(document).on('click', 'a', function(event) { 
        event.stopPropagation();
    })

    $(document).on('click', '.card', function() { 
        let key = $(this).data('key');
        window.location.href = 'viewer?viewer__current_corpus='+key;
    });

  	$('[data-toggle="tooltip"]').tooltip();
});