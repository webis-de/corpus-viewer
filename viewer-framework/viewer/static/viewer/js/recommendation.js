class Recommendation
{
    constructor(passed_context, passed_id_input, passed_id_wrapper, passed_callback = undefined, passed_url = '')
    {
        this.m_context = passed_context;

        this.m_id_input = passed_id_input;
        this.m_input = $(passed_id_input);

        this.m_id_wrapper = passed_id_wrapper;
        this.m_wrapper = $(passed_id_wrapper);

        this.m_callback = passed_callback;
        this.m_url = passed_url;

        this.m_length_current_recommendations = 0;
        this.m_index_position = -1;
        this.m_mouse_over_wrapper = false;

        this.m_template_recommendations = `
            <div class="recommendation" data-tag_id="PLACEHOLDER_ID" data-tag_name="PLACEHOLDER_NAME" data-tag_color="PLACEHOLDER_COLOR">
                <div class="tag_marker_recommendation" style="background-color: PLACEHOLDER_COLOR;"></div>
                PLACEHOLDER_NAME
            </div>`;

        this.init_events();

        this.init_styles();
    }

    init_styles()
    {
        let css_wrapper = `
            PLACEHOLDER_ID_WRAPPER {
                display: none;
                position: absolute;
                width: 100%;
                border-radius: 6px;
                border: 1px solid black;
                padding: 0 5px;
                background-color: #f8f8f8;
                z-index: 4444;
            }
        `;
        css_wrapper = css_wrapper.replace('PLACEHOLDER_ID_WRAPPER', this.m_id_wrapper);

        let css_recommendation = `
            PLACEHOLDER_ID_WRAPPER .recommendation {
                margin-top: 5px;
                margin-bottom: 5px;
                cursor: pointer;

                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }
            
        `;
        css_recommendation = css_recommendation.replace(/PLACEHOLDER_ID_WRAPPER/g, this.m_id_wrapper);
        
        // PLACEHOLDER_ID_WRAPPER .recommendation:hover {
        //         background-color: #ccc;
            // }
        let css_tag_marker_recommendation = `
            PLACEHOLDER_ID_WRAPPER .tag_marker_recommendation {
                float: left;
                width: 10px;
                height: 24px;
                margin-right: 5px;
            }
        `;
        css_tag_marker_recommendation = css_tag_marker_recommendation.replace('PLACEHOLDER_ID_WRAPPER', this.m_id_wrapper);

        $('head').append(
            '<style>'+
            css_wrapper+
            css_recommendation+
            css_tag_marker_recommendation+
            '</style>'
        );
    }

    init_events()
    {
        $(this.m_context).on('input', this.m_id_input, this, function(event){
            event.data.request_recommendation($(this))
        });

        $(this.m_context).on('click', this.m_id_wrapper + ' .recommendation', this, function(event){
            event.data.handle_click_on_recommendation($(this))
        });

        $(this.m_context).on('mouseenter', this.m_id_wrapper, this, function(event){
            event.data.m_mouse_over_wrapper = true;
        });

        $(this.m_context).on('mouseleave', this.m_id_wrapper, this, function(event){
            event.data.m_mouse_over_wrapper = false;
        });

        $(this.m_context).on('mouseenter', this.m_id_wrapper + ' .recommendation', this, function(event){
            // event.data.request_recommendation($(this))
            $(event.data.m_id_wrapper + ' .recommendation').css('background-color', '');
            
            event.data.m_index_position = $(this).index();
            $(event.data.m_id_wrapper + ' .recommendation:nth-child(' + (event.data.m_index_position + 1) + ')').css('background-color', '#ccc')
            // console.log($(this).index());

        });

        $(this.m_context).on('keydown', this.m_id_input, this, function(event) {
            let that = event.data;
            switch(event.which)
            {
                case 38:
                    that.move_up();
                    break;
                case 40:
                    that.move_down();
                    break;
                case 13:
                    if(that.m_index_position > -1)
                    {
                        event.preventDefault();
                        that.handle_click_on_recommendation($(that.m_id_wrapper + ' .recommendation:nth-child(' + (that.m_index_position + 1) + ')'))
                    }
                    break;
                default:
                    break;
            }
        })

        $(this.m_context).on('blur', this.m_id_input, this, function(event){
            if(!event.data.m_mouse_over_wrapper)
            {
                event.data.remove_wrapper_recommendation();
            }
        });

        $(this.m_context).on('focus', this.m_id_input, this, function(event){
            event.data.request_recommendation($(this));
        });
    }

    move_up()
    {
        if(this.m_length_current_recommendations > 0)
        {
            this.m_index_position = this.m_index_position - 1;
            if(this.m_index_position < 0)
            {
                this.m_index_position = this.m_length_current_recommendations - 1;
            }

            $(this.m_id_wrapper + ' .recommendation').css('background-color', '');
            $(this.m_id_wrapper + ' .recommendation:nth-child(' + (this.m_index_position + 1) + ')').css('background-color', '#ccc')
        }
    }

    move_down()
    {
        if(this.m_length_current_recommendations > 0)
        {
            this.m_index_position = (this.m_index_position + 1) % this.m_length_current_recommendations;
            $(this.m_id_wrapper + ' .recommendation').css('background-color', '');
            $(this.m_id_wrapper + ' .recommendation:nth-child(' + (this.m_index_position + 1) + ')').css('background-color', '#ccc')
        }
    }

    request_recommendation(input)
    {
        let instance = this;
        let tag_name = input.val();
        if(tag_name == '')
        {
            this.remove_wrapper_recommendation();
        } else {
            let data = {};
            data.task = 'get_tag_recommendations';
            data.tag_name = tag_name;

            $.ajax({
                url: this.m_url,
                method: 'POST',
                contentType: 'application/json',
                headers: {'X-CSRFToken':$('input[name="csrfmiddlewaretoken"]').val()},
                data: JSON.stringify(data),
                success: function(result) {
                    instance.set_recommendations($(result.data.array_recommendations));
                },
                error: function(result) {
                    error_corpus_not_exists();
                }
            });
        }
    }

    handle_click_on_recommendation(recommendation)
    {
        if(this.m_callback != undefined)
        {
            this.m_callback(recommendation, this.m_input);
        }

        this.remove_wrapper_recommendation();
    }

    remove_wrapper_recommendation()
    {
        this.m_mouse_over_wrapper = false;
        this.m_wrapper.hide();
        this.reset_recommendations();
    }

    set_recommendations(array_recommendations)
    {
        this.reset_recommendations(this.m_wrapper);

        this.m_length_current_recommendations = array_recommendations.length;
        this.m_index_position = -1;

        let instance = this;
        array_recommendations.each(function() {
            instance.m_wrapper.append(
                instance.m_template_recommendations
                .replace('PLACEHOLDER_ID', this.id)
                .replace(/PLACEHOLDER_NAME/g, this.name)
                .replace(/PLACEHOLDER_COLOR/g, this.color)
            );
        });

        if(array_recommendations.length != 0)
        {
            this.m_wrapper.show();
        } else {
            this.m_wrapper.hide();
        }
    }

    reset_recommendations()
    {
        this.m_length_current_recommendations = 0;
        this.m_index_position = -1;
        this.m_wrapper.find('.recommendation').remove();
    }
}