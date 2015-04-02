// admin-modal.js, admin GUI generic modal functions
// requires: jquery

function modal_error_show(event, msg) {
    $(this).find('.modal-error .modal-msg').html(msg);
    $(this).find('.modal-error').show();    
}

function modal_error_hide(event, msg) {
    $(this).find('.modal-error .modal-msg').html('');
    $(this).find('.modal-error').hide();         
}

function modal_success_show(event, msg) {
    if(msg) {
        $(this).find('.modal-success .modal-msg').html(msg);
    }
    $(this).find('.modal-success').show();    
}

function modal_success_hide(event) {
    $(this).find('.modal-success').hide();         
}

function modal_progress_show(event, msg) {
    $(this).find('.modal-progress .modal-msg').html(msg);
    $(this).find('.modal-progress').show();    
}

function modal_progress_hide(event) {
    $(this).find('.modal-progress').hide(); 
}

function modal_confirm_show(event, msg, callback) { 
    var $panel = $(this).find('.modal-confirm');
    
    $panel.find('.modal-msg').html(msg);
    
    $panel.find('.btn').on('click.confirm', function(event) {
        $(this).off('click.confirm'); 
        $panel.hide();         
        callback($(this).hasClass('btn-primary'));
    });
    
    $panel.show();    
}

function modal_confirm_hide(event) {
    $(this).find('.modal-confirm').hide(); 
}

function modal_input_show(event, msg, callback) {
    var $panel = $(this).find('.modal-input');
    $panel.find('.modal-msg').html(msg);
    
    var $input = $panel.find('input[type="text"]').val('');
    $input.closest('.form-group').removeClass('has-error');
    
    $panel.find('.btn').on('click.confirm', function(event) {
        var yes = $(this).hasClass('btn-primary');
        var val = $input.trimmed();
        
        if(yes && !val) {
            $input.focus().closest('.form-group').addClass('has-error');
            return;
        } 

        $(this).off('click.confirm'); 
        $panel.hide();         
        callback(yes, val);
    });
    
    $panel.show();    
}

function modal_input_hide(event) {
    $(this).find('.modal-input').hide();
}

function modal_all_hide(event) {
    $(this).find('.modal-error, .modal-success, .modal-progress, .modal-confirm, .modal-input').hide();
}

// Add generic event handlers to a modal
function modal_init($modal) {
    return $modal
        .on('error_show', modal_error_show)
        .on('error_hide', modal_error_hide)
        .on('success_show', modal_success_show)
        .on('success_hide', modal_success_hide)
        .on('progress_show', modal_progress_show)
        .on('progress_hide', modal_progress_hide)
        .on('confirm_show', modal_confirm_show)
        .on('confirm_hide', modal_confirm_hide)
        .on('input_show', modal_input_show)
        .on('input_hide', modal_input_show)
        .on('all_hide', modal_all_hide);
}
