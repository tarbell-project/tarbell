// required jquery, json2

//
// extend jquery
//

(function($) {

$.fn.extend({
    // enable UI element
    enable: function() {
        return this.removeAttr('disabled');
    },
    // disable UI element
    disable: function() {
        return this.attr('disabled', 'disabled'); 
    }
});

})(jQuery);


//
// templates
//

/*var _config_s3_bucket_template = _.template($('#config_s3_bucket_template').html());
var _select_bucket_template = _.template($('#select_bucket_template').html());
var _select_blueprint_template = _.template($('#select_blueprint_template').html());
var _error_alert_template = _.template($('#error_alert_template').html());
var _success_alert_template = _.template($('#success_alert_template').html());
var _blueprint_template = _.template($('#blueprint_template').html());
var _project_template = _.template($('#project_template').html());
var _detail_s3_bucket_template = _.template($('#detail_s3_bucket_template').html());
*/
//
// generic modal event handlers
//

modal_error_show = function(event, msg) {
    $(this).find('.modal-error .modal-msg').html(msg);
    $(this).find('.modal-error').show();    
};
modal_error_hide = function(event, msg) {
    $(this).find('.modal-error .modal-msg').html('');
    $(this).find('.modal-error').hide();         
};

modal_success_show = function(event, msg) {
    if(msg) {
        $(this).find('.modal-success .modal-msg').html(msg);
    }
    $(this).find('.modal-success').show();    
};

modal_success_hide = function(event) {
    $(this).find('.modal-success').hide();         
};

modal_progress_show = function(event, msg) {
    $(this).find('.modal-progress .modal-msg').html(msg);
    $(this).find('.modal-progress').show();    
};

modal_progress_hide = function(event) {
    $(this).find('.modal-progress').hide(); 
};

modal_confirm_show = function(event, msg, callback) { 
    console.log('modal_confirm_show');
       
    var $panel = $(this).find('.modal-confirm');
    console.log(callback);
    
    $panel.find('.modal-msg').html(msg);
    
    $panel.find('.btn').bind('click.confirm', function(event) {
        $(this).unbind('click.confirm'); 
        $panel.hide();         
        callback($(this).hasClass('btn-primary'));
    });
    
    $panel.show();    
};

modal_confirm_hide = function(event) {
    $(this).find('.modal-confirm').hide(); 
};

function modal_init($modal) {
    return $modal
        .on('error_show', modal_error_show)
        .on('error_hide', modal_error_hide)
        .on('success_show', modal_success_show)
        .on('success_hide', modal_success_hide)
        .on('progress_show', modal_progress_show)
        .on('progress_hide', modal_progress_hide)
        .on('confirm_show', modal_confirm_show)
        .on('confirm_hide', modal_confirm_hide);
}


//
// debug
//

function debug() {
    if(console && console.log) {
        // converts arguments to real array
        var args = Array.prototype.slice.call(arguments);
        args.unshift('**');
        console.log.apply(console, args); // call the function
    }
}

//
// alerts
//

function alert_hide() {
    $('div.tab-pane').find('div[role="alert"]').remove(); // all
}

function error_hide() {
    $('div.tab-pane').find('div[role="alert"].alert-danger').remove();   
}

function error_alert(message) {
    error_hide();
    $('div.tab-pane.active').prepend(_error_alert_template({message: message}));    
}

function success_hide() {
    $('div.tab-pane').find('div[role="alert"].alert-success').remove();   
}

function success_alert(message) {
    success_hide();
    $('div.tab-pane.active').prepend(_success_alert_template({message: message}));    
}

//
// progress
//

function progress_show(msg) {
    $('#progress_modal .modal-msg').html(msg);
    $('#progress_modal').modal('show');
}

function progress_hide() {
    $('#progress_modal').modal('hide');
}

//
// ajax
//

function _ajax(url, type, data, on_error, on_success, on_complete) {
    var _error = '';
    
    debug('ajax params', data);
    
    $.ajax({
        url: url,
        type: type,
        data: data,
        dataType: 'json',
        timeout: 45000, // ms
        error: function(xhr, status, err) { 
            _error = err || status;
            debug('ajax error', _error);           
            on_error(_error);
        },
        success: function(data) {
            debug('ajax data', data);
            if(data.error) {
                _error = data.error;
                on_error(_error);
            } else if (on_success) {
                on_success(data);
            }
        },
        complete: function() {
            if(on_complete) {
                on_complete(_error);
            }
        }
    });
}

function ajax_get(url, data, on_error, on_success, on_complete) {
    _ajax(url, 'GET', data, on_error, on_success, on_complete);
}

function ajax_post(url, data, on_error, on_success, on_complete) {
    _ajax(url, 'POST', data, on_error, on_success, on_complete);
}

//
// config
//

function config_dirty() {
    $('#config_save').enable();
}

function disable_bucket(target) {
    var $group = $(target).closest('.form-group');
    $group.find('input').disable();
    $group.find('.remove-bucket').hide();
    $group.find('.add-bucket').show();
    config_dirty();
}

function enable_bucket(target) {
    var $group = $(target).closest('.form-group');
    $group.find('input').enable();
    $group.find('.add-bucket').hide();
    $group.find('.remove-bucket').show();
}

function remove_bucket(target) {
    $(target).closest('.form-group').remove();
}


$(function() {

    //
    // Clear alerts/states when switching from tab to tab
    //
    $('a[data-toggle="tab"]').on('hide.bs.tab', function(event) {      
        alert_hide();
        $('.form-group, .input-group').removeClass('has-error');        
        $('#blueprint_url, #project_url').val('');
    });
     
// ------------------------------------------------------------
// settings tab
// ------------------------------------------------------------
     
    $('#configuration_tab input').change(config_dirty);
        
    $('#config_add_bucket').click(function(event) {
        var $group = $(this).closest('.form-group');
        $(_config_s3_bucket_template())
            .insertAfter($group)
            .find('input')
                .change(config_dirty);
    });
             
      
    $('#settings_save').click(function(event) {
         progress_show('Saving configuration');
         
         ajax_get('/configuration/save/', {},// TODO: add data
            function(error) {
                error_alert(error);
            },
            function(data) {
                // TODO: update cached config
            },
            function() {
                progress_hide();
            });
    });
 
// ------------------------------------------------------------
// blueprints
// ------------------------------------------------------------
  
    $('#blueprint_install').click(function(event) {
        alert_hide();
        
        var url = $('#blueprint_url').val().trim();
        if(!url) {
            $(this).closest('.input-group').addClass('has-error');
            return;
        }
        
        $(this).closest('.input-group').removeClass('has-error');           
        progress_show('Installing blueprint'); 
             
        ajax_get('/blueprint/install/', {url: url},
            function(error) {
                error_alert(error);
            },
            function(data) {
                // Add to cached config!
                _config['project_templates'].push(data);
                
                $('#blueprints_table tbody').append(_blueprint_template(data));
                $('#blueprint_url').val('');
                success_alert('Successfully installed blueprint <strong>'+data.name+'</strong>');                               
            },
            function() {
                progress_hide();
            });
    });
    
// ------------------------------------------------------------
// projects tab
// ------------------------------------------------------------ 
   

// ------------------------------------------------------------
// common modal
// ------------------------------------------------------------
    
    $('#run_modal')
        .on('show.bs.modal', function(event) {
            var directory = $(event.relatedTarget)
                .closest('tr').attr('data-project');
            $(this).data('data-project', directory);      
            $('.project-name').html(directory);
        });

// ------------------------------------------------------------
// run modal
// ------------------------------------------------------------

    modal_init($('#run_modal'))
        .on('reset', function(event) {
            $('#run_address').enable()
                .closest('.form-group').removeClass('has-error');              
            $('#run_stop_button').hide();
            $('#run_done_button, #run_button').show();   
        })
        .on('show.bs.modal', function(event) {
            $(this)
                .trigger('error_hide')
                .trigger('progress_hide')
                .trigger('reset');
            $('#run_address').val('127.0.0.1:5000');
         });      
        
    $('#run_button').click(function(event) {
        var $modal = $(this).closest('.modal').trigger('error_hide');
        var project = $modal.data('data-project');
               
        var $address = $('#run_address');
        var address = $address.val().trim();
        if(!address) {
            $address.focus().closest('.form-group').addClass('has-error');
            return;
        }
               
        $address.closest('.form-group').removeClass('has-error');
        $modal.trigger('progress_show', 'Starting preview server');
        
        ajax_get('/project/run/', {
                project: project,
                address: address
            }, 
            function(error) {
                $modal.trigger('error_show', error);
            },
            function(data) {
                window.open('http://'+address);
                
                $('#run_address').disable();
                $('#run_done_button, #run_button').hide();   
                $('#run_stop_button').show();
            },
            function() {
                $modal.trigger('progress_hide');
            }
        );
    });
    
    $('#run_stop_button').click(function(event) {
        ajax_get('/project/stop/', {}, 
            function(error) {
                $modal.trigger('error_show', error);
            },
            function(data) {
                $('#run_modal').trigger('reset');
            }
        );
    });  
     
});