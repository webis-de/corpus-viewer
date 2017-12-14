$(document).ready(function()
{
    $(document).on('click', '#submit_refresh_corpora', function(event) {
        $('#submit_refresh_corpora').blur();
        refresh_corpora();
    });

    $(document).on('click', '.card_corpus a', function(event) { 
        event.stopPropagation();
    })

    $(document).on('click auxclick', '.card', function(event) { 
        let key = $(this).data('key');

        // const url = 'viewer?viewer__current_corpus='+key;
        const url = 'viewer/'+key;

        switch(event.which)
        {
            case 1:
                window.location.href = url;
                break;
            case 2:
                window.open(url);
                break;
        }
    });
  	load_corpora();

});

let glob_template_corpus = `
    <div class="col-sm-6 col-md-4 col-lg-3 mt-3">
        <div class="card card_corpus" data-key="PLACEHOLDER_ID_CORPUS">
            <h3 class="card-header">
                PLACEHOLDER_LOCKED
                PLACEHOLDER_NAME
                PLACEHOLDER_STATE_LOADED
            </h3>                
            <div class="card-body">
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

let glob_template_alert_exception_linenumber = `
    <div class="alert alert-danger" role="alert">
        The file <b>PLACEHOLDER_FILE</b> has incorrect syntax at line PLACEHOLDER_EXCEPTION!<br>
    </div>`

let glob_template_alert_exception = `
    <div class="alert alert-danger" role="alert">
        The file <b>PLACEHOLDER_FILE</b> threw the following exception:<br>PLACEHOLDER_EXCEPTION!<br>
    </div>`

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

function get_html_locked(has_secret_token)
{
    if(has_secret_token)
    {
        return '<i class="fa fa-lock" aria-hidden="true"></i>'
    }
    else
    {
        return ''
    }
}

function update_corpora_cards(corpora)
{
    const wrapper_corpora = $('#wrapper_corpora');
    
    wrapper_corpora.html('');

    $.each(corpora, function(id_corpus, corpus) {
        wrapper_corpora.append(
            glob_template_corpus
                .replace('PLACEHOLDER_ID_CORPUS', id_corpus)
                .replace('PLACEHOLDER_NAME', corpus.name)
                .replace('PLACEHOLDER_DESCRIPTION', corpus.description)
                .replace('PLACEHOLDER_STATE_LOADED', '')
                // .replace('PLACEHOLDER_STATE_LOADED', get_html_state_loaded(corpus.state_loaded))
                .replace('PLACEHOLDER_LOCKED', get_html_locked(corpus.has_secret_token))
        );
    });

    $('[data-toggle="tooltip"]').tooltip();
}

function update_corpora_with_exceptions(corpora)
{
    const wrapper_corpora = $('#wrapper_corpora_with_exceptions')

    wrapper_corpora.html('');
    
    $.each(corpora, function(id_corpus, exception) {
        let exception_processed = exception;
        // let exception_processed = exception.replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/ /g, '&nbsp;').replace(/\n/g, '<br>');
        if(!isNaN(parseFloat(exception_processed))) {
            wrapper_corpora.append(glob_template_alert_exception_linenumber
                .replace('PLACEHOLDER_FILE', id_corpus+'.py')
                .replace('PLACEHOLDER_EXCEPTION', exception_processed)
            );
        } else {
            wrapper_corpora.append(glob_template_alert_exception
                .replace('PLACEHOLDER_FILE', id_corpus+'.py')
                .replace('PLACEHOLDER_EXCEPTION', exception_processed)
            );
        }
    });
}

function refresh_corpora()
{
    let data = {};
    data.task = 'refresh_corpora';

    $.ajax({
        method: 'POST',
        contentType: 'application/json',
        headers: {'X-CSRFToken':$('input[name="csrfmiddlewaretoken"]').val()},
        data: JSON.stringify(data),
        success: function(result) {
            update_corpora_cards(result.data.corpora);
            update_corpora_with_exceptions(result.data.corpora_with_exceptions);
        }
    });   
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
            update_corpora_cards(result.data.corpora);
            update_corpora_with_exceptions(result.data.corpora_with_exceptions);
        }
    });

}

function set_session_entry(session_key, session_value, callback)
{
    let data = {};
    data.task = "set_session_entry";
    data.session_key = session_key;
    data.session_value = session_value;

    $.ajax({
        method: 'POST',
        contentType: 'application/json',
        headers: {'X-CSRFToken':$('input[name="csrfmiddlewaretoken"]').val()},
        data: JSON.stringify(data),
        success: function(result) {
            if(callback != undefined)
            {
                callback()
            }
        },
        error: function(result) {
            error_corpus_not_exists();
        }
    });
}