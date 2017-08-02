$(document).ready(function()
{
    $(document).on('click', 'a', function(event) { 
        event.stopPropagation();
    })

    $(document).on('click', '.card', function() { 
        let key = $(this).data('key');
        window.location.href = 'viewer?viewer__current_corpus='+key;
    });

  	load_corpora();
});

let glob_template_corpus = `
    <div class="col-sm-6 col-md-4 col-lg-3 mb-3">
        <div class="card card_corpus" data-key="PLACEHOLDER_ID_CORPUS">
            <h3 class="card-header">
                <span>PLACEHOLDER_NAME</span>
                PLACEHOLDER_STATE_LOADED
            </h3>                
            <div class="card-block">
                <p class="card-text">
                    PLACEHOLDER_DESCRIPTION
                </p>
            </div>
            <!-- <div class="card-footer">
                <small class="text-muted">Last updated 3 mins ago</small>
            </div> -->
        </div>
    </div>`;

let glob_template_state_loaded = `
    <span class="pull-right align-middle PLACEHOLDER_COLOR" data-toggle="tooltip" data-placement="top" title="PLACEHOLDER_TOOLTIP">
        <span class="fa-stack" style="font-size: 0.4em">
            <i class="fa fa-square-o fa-stack-2x"></i>
            <i class="fa PLACEHOLDER_ICON fa-stack-1x" style="top: -1px;"></i>
        </span>
    </span>`

function get_html_state_loaded(state) 
{
    if(state == 0) 
    {
        return glob_template_state_loaded
            .replace('PLACEHOLDER_COLOR', 'text-success')
            .replace('PLACEHOLDER_ICON', 'fa-check')
            .replace('PLACEHOLDER_TOOLTIP', 'Indexed')
    }
    else if(state == 1)
    {
        return glob_template_state_loaded
            .replace('PLACEHOLDER_COLOR', 'text-danger')
            .replace('PLACEHOLDER_ICON', 'fa-times')
            .replace('PLACEHOLDER_TOOLTIP', 'Not indexed')
    }
    else if(state == 2)
    {
        return glob_template_state_loaded
            .replace('PLACEHOLDER_COLOR', 'text-warning')
            .replace('PLACEHOLDER_ICON', 'fa-refresh fa-spin')
            .replace('PLACEHOLDER_TOOLTIP', 'Currently Indexing')
    }
}

function load_corpora() 
{
	let data = {};
    data.task = 'get_corpora';

    $.ajax({
        method: 'POST',
        contentType: 'application/json',
        headers: {'X-CSRFToken':$('input[name="csrfmiddlewaretoken"]').val()},
        data: JSON.stringify(data),
        success: function(result) {
            let wrapper_corpora = $('#wrapper_corpora');

            $.each(result.data.corpora, function(id_corpus, corpus) {
                wrapper_corpora.append(
                    glob_template_corpus
                        .replace('PLACEHOLDER_ID_CORPUS', id_corpus)
                        .replace('PLACEHOLDER_NAME', corpus.name)
                        .replace('PLACEHOLDER_DESCRIPTION', corpus.description)
                        .replace('PLACEHOLDER_STATE_LOADED', get_html_state_loaded(corpus.state_loaded))
                );
            });

            $('[data-toggle="tooltip"]').tooltip();
        }
    });

}