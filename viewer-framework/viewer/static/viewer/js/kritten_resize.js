class Kritten_Resize
{
	constructor(passed_column_left, passed_column_right)
	{
		// this.m_id_column_resized = passed_id_column_resized;	
		// this.m_id_column_pasive = passed_id_column_pasive;

		this.m_column_resized = passed_column_left;
		this.m_column_passive = passed_column_right;

		this.m_row = this.m_column_passive.parent();

		this.m_slider = undefined;
		this.m_indicate_hide_filters = false;
		this.m_width_start = undefined;
		this.m_width_current = undefined;
		this.m_width_last = undefined;
		this.m_mouse_start = undefined;

        this.init_styles();

		this.init_content();

        this.init_events();
	}

	init_content()
	{
		this.m_slider = $(`
        	<div class="resizeable_slider_wrapper">
        		<div class="resizeable_slider"></div>
    		</div>
		`);
		this.m_column_resized.prepend(this.m_slider);
	}

    init_events()
    {
		$(document).on('pointerdown', '.resizeable_slider_wrapper', this,  this.mousedown);
		$(document).on('pointerdown', '.resizeable_show', this,  this.click);
    }

    init_styles()
    {
    	const css_column_resized = `
	    	.kritten_resize_left {
	    		max-width: 100%;
			}
    	`;
    	const css_slider = `
	    	.resizeable_slider_wrapper {
				position: absolute; 
				right: 0px; 
				z-index: 3; 

	    		width: 26px;
				height: 100%; 

				padding: 10px 11px;
				cursor: col-resize;

	    		touch-action: none;
	    		right: -13px;
	    	}

	    	.resizeable_slider {
	    		background-color: rgba(0, 0, 0, 0.2);
				height: 100%;	    		
				width: 100%;	    		
			}
    	`;
   //  	const css_slider = `
	  //   	.resizeable_slider {
			// 	border-left: 4px solid rgba(0, 0, 0, 0.2);
			// 	height: calc(100% - 20px); 
			// 	top: 10px; 
			// 	position: absolute; 
			// 	z-index: 3; 
			// 	right: -2px; 
			// 	cursor: col-resize;
				
	  //   		touch-action: none;
			// }
   //  	`;
    	const css_show = `
	    	.resizeable_show {
				border-left: 10px solid rgba(0, 0, 0, 0.2);
				border-top: 10px solid transparent;
				border-bottom: 10px solid transparent;
				min-height: 90vh;
				height: calc(100% - 20px); 
				top: 10px; 
				z-index: 3; 
				position: absolute; 
				cursor: pointer;
				left: 0px; 

			}
	    	.resizeable_show:hover {
				border-left: 10px solid rgba(0, 0, 0, 0.3);
				border-top: 10px solid transparent;
				border-bottom: 10px solid transparent;
			}
    	`;

        $('head').append(`
            <style>
	            ${css_slider}
	            ${css_show}
	            ${css_column_resized}
            </style>
        `);
    }

	mousedown(event)
	{
		// console.log('mousedown');
		// console.log(event)
		$('body').css('user-select', 'none');
		event.data.m_width_start = event.data.m_column_resized.outerWidth();
		event.data.m_column_resized.css('flex-grow', 0);
		event.data.m_column_resized.css('flex-basis', event.data.m_width_start);
		event.data.m_width_current = event.data.m_width_start;
		event.data.m_mouse_start = event.pageX;

		$(document).on('pointermove', event.data, event.data.mousemove);
		$(document).on('pointerup', event.data, event.data.mouseup);
	}

	mousemove(event)
	{
		// console.log('mousemove');
		// console.log(event.pageX);

		// let delta_x = event.pageX;
		// if(delta_x == undefined)
		// {
		// 	delta_x = event.originalEvent.touches[0].pageX;
		// }

		const flex_basis = event.data.m_width_start;
		let width_new = flex_basis + (event.pageX - event.data.m_mouse_start);

		// indicate possibility to hide filters
		if(width_new <= 100)
		{
			if(!event.data.m_indicate_hide_filters)
			{
				event.data.m_indicate_hide_filters = true;
				event.data.m_slider.css('right', 296);
				event.data.m_column_resized.css('opacity', 0.3)
			}
		} else {
			if(event.data.m_indicate_hide_filters)
			{
				event.data.m_slider.css('right', -13);
				event.data.m_indicate_hide_filters = false;
				event.data.m_column_resized.css('opacity', 1)

			}
			// console.log('greater')
		}

		width_new = Math.max(300, width_new);
		// console.log(width_new)
		event.data.m_column_resized.css('flex-basis', width_new);
		if(event.data.m_column_passive.width() + event.data.m_column_resized.width() < event.data.m_row.width())
		{
			event.data.m_width_current = width_new;
		} else {
			event.data.m_column_resized.css('flex-basis', event.data.m_width_current);
		}
	}

	click(event)
	{
		// console.log('click');
		if(event.data.m_width_last == undefined)
		{
			event.data.m_width_last = 300;
		}
		console.log(event.data.m_width_last)
		event.data.m_column_resized.css('flex-basis', event.data.m_width_last);
		set_session_entry('width_filters', event.data.m_width_last);

		event.data.m_column_resized.css('opacity', 1)
		event.data.m_column_resized.show();
		$(this).remove();
		event.data.m_slider.css('right', -13);
	}

	mouseup(event)
	{
		// console.log('mouseup');
		if(event.data.m_indicate_hide_filters)
		{
			event.data.m_column_resized.hide();
			event.data.m_column_passive.prepend(
				`<div class="resizeable_show"></div>`
			);

			set_session_entry('width_filters', false);
		} else {
			event.data.m_width_last = event.data.m_width_current;
			set_session_entry('width_filters', event.data.m_width_current);
		}

		$('body').css('user-select', '')
		$(document).off('pointermove', event.data.mousemove);
		$(document).off('pointerup', event.data.mouseup);
	}
}

class Kritten_Resize_Manager
{
	constructor()
	{
        this.init();
	}

	init()
	{
		$('[data-kritten_resize]').each(function(i, element) {
			const row = $(element);

			const columns = row.children();
			if(columns.length != 2) 
			{
				return;
			} else {
				const column_left = $(columns[0]);
				const column_right = $(columns[1]);

				if(row.width() - column_left.width() > 50)
				{
					column_left.addClass('kritten_resize_left');
					column_right.addClass('kritten_resize_right');
					const kritten_resize = new Kritten_Resize(column_left, column_right);
				}
			}
		});
	}
}

const kritten_resize_manager = new Kritten_Resize_Manager();
