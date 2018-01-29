$('head').append(
`
<style>
	.kritten_resizeable {
		border-left: 4px solid rgba(0, 0, 0, 0.2);
		height: calc(100% - 20px); 
		top: 10px; 
		position: absolute; 
		z-index: 3; 
		right: -2px; 
		cursor: col-resize;
	}
	.kritten_open {
		border-left: 10px solid rgba(0, 0, 0, 0.2);
		border-top: 10px solid transparent;
		border-bottom: 10px solid transparent;
		height: calc(100% - 20px); 
		top: 10px; 
		z-index: 3; 
		position: absolute; 
		cursor: pointer;
		left: 0px; 

	}
	.kritten_open:hover {
		border-left: 10px solid rgba(0, 0, 0, 0.3);
		border-top: 10px solid transparent;
		border-bottom: 10px solid transparent;
		// border-color: rgba(0, 0, 0, 0.3)
	}
</style>
`
);

$(document).ready(function()
{
	const draggable = $('.kritten_resizeable')
	const parent_draggable = draggable.parent();
	const row = parent_draggable.parent();
	const next_parent_draggable = parent_draggable.next();
	parent_draggable.css('max-width', '100%')
	// $(document).on('ondrag', '.kritten_resizeable', function(e) {

	let x = undefined;
	let indicate_hide_filters = false;
	let global_width_start = undefined;
	let global_width_current = undefined;
	let global_width_last = undefined;

	
function mousedown(e)
{
	$('body').css('user-select', 'none');
	global_width_start = parent_draggable.outerWidth();
	parent_draggable.css('flex-grow', 0);
	parent_draggable.css('flex-basis', global_width_start);
	x = e.pageX;
	global_width_current = global_width_start;

	$(document).on('mousemove', mousemove);

	$(document).on('mouseup', mouseup);
}

function mousemove(e)
{
	let flex_basis = global_width_start;
	let width_new = flex_basis + (e.pageX - x);

	// indicate possibility to hide filters
	if(width_new <= 100)
	{
		if(!indicate_hide_filters)
		{
			indicate_hide_filters = true;
			draggable.css('right', 296);
			parent_draggable.css('opacity', 0.3)
		}
	} else {
		if(indicate_hide_filters)
		{
			draggable.css('right', -2);
			indicate_hide_filters = false;
			parent_draggable.css('opacity', 1)

		}
	}

	width_new = Math.max(300, width_new);
	parent_draggable.css('flex-basis', width_new);
	if(next_parent_draggable.width() + parent_draggable.width() < row.width())
	{
		global_width_current = width_new;
	} else {
		parent_draggable.css('flex-basis', global_width_current);
	}
}

function click()
{
	if(global_width_last == undefined)
	{
		global_width_last = 300;
	}
	parent_draggable.css('flex-basis', global_width_last);
	set_session_entry('width_filters', global_width_last);

	parent_draggable.css('opacity', 1)
	parent_draggable.show();
	$(this).remove();
	draggable.css('right', -2);
}

function mouseup()
{
	if(indicate_hide_filters)
	{
		parent_draggable.hide();
		next_parent_draggable.prepend(
			`<div class="kritten_open"></div>`
		);

		set_session_entry('width_filters', false);
	} else {
		global_width_last = global_width_current;
		set_session_entry('width_filters', global_width_current);
	}

	$('body').css('user-select', '')
	$(document).off('mousemove', mousemove);
	$(document).off('mouseup', mouseup);
}

$(document).on('mousedown', '.kritten_resizeable', mousedown);
$(document).on('click', '.kritten_open', click);	

});
