// admin-util.js, admin GUI utility functions
// requires: jquery, json2

function debug() {
    if(console && console.log) {
        // converts arguments to real array
        var args = Array.prototype.slice.call(arguments);
        args.unshift('**');
        console.log.apply(console, args); // call the function
    }
}

// polyfill
Object.keys=Object.keys||function(o,k,r){r=[];for(k in o)r.hasOwnProperty.call(o,k)&&r.push(k);return r};
 
// extend jquery
(function($) {
    $.fn.extend({
        // enable UI element
        enable: function() {
            return this.removeAttr('disabled');
        },
        // disable UI element
        disable: function() {
            return this.attr('disabled', 'disabled'); 
        },
        // get form input trimmed value 
        trimmed: function() {
            return this.val().trim();
        }
    });
})(jQuery);

// ajax
function _ajax(url, type, data, on_error, on_success, on_complete) {
    debug('ajax params', data);
    var _error = '';
        
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
