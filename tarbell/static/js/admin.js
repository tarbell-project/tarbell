// admin.js, admin GUI functions
// required jquery, json2

//
// templates
//

var _error_alert_template = _.template($('#error_alert_template').html());
var _success_alert_template = _.template($('#success_alert_template').html());

var _google_msg_template = _.template($('#google_msg_template').html());

var _add_bucket_template = _.template($('#add_bucket_template').html());

//
// progress modal
//

function progress_show(msg) {
    $('#progress_modal .modal-msg').html(msg);
    $('#progress_modal').modal('show');
}

function progress_hide() {
    $('#progress_modal').modal('hide');
}

//
// input modal
//

function input_show(msg, callback) {
    var $input = $('#input_modal').find('input[type="text"]');

    var $input_modal = $('#input_modal')
        .on('show.bs.modal', function(event) {
            $input_modal.find('.modal-msg').html(msg);
            $input.val('');
        })
        .on('click', '.cancel', function(event) {
            $input_modal.modal('hide');
            callback(false);
        })
        .on('click', '.submit', function(event) {
            var value = $input.trimmed();
            if(!value) {
                $input.focus()
                    .closest('.form-group').addClass('has-error');
                return;
            }

            $input_modal.modal('hide');
            callback(true, value);
        });

    $input_modal.modal('show');
}

function input_hide() {
    $('#input_modal').modal('hide');
}

//
// alerts
//

function alert_hide() {
    $('div.tab-pane').find('div[role="alert"].alert-danger, div[role="alert"].alert-success').remove(); 
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
// settings
//

function settings_dirty() {
    $('#settings_save').enable();
}

// Enable row of S3 bucket controls
function bucket_enable(target) {
    var $group = $(target).closest('.form-group');
    $group.find('input').enable();
    $group.find('.bucket-enable').hide();
    $group.find('.bucket-disable').show();
    $group.removeClass('disabled');
}

// Remove set of S3 bucket controls
function bucket_remove(target) {
    $(target).closest('.form-group').remove();
}

// Add set of S3 bucket controls
function bucket_add(target, data, tmpl) {
    var d = $.extend(
        {name: '', access_key_id: '', secret_access_key: ''},
        data || {}
    );
    var $group = $(target).closest('.form-group');
    var tmpl = tmpl || _add_bucket_template;
    $(tmpl(d)).insertBefore($group);
}


// Get and validate S3 defaults
function get_s3_defaults(cfg) {
    var key = $('#default-s3-access-key-id').trimmed();
    var secret = $('#default-s3-secret-access-key').trimmed();
    var staging = $('#default-s3-buckets-staging').trimmed();
    var production = $('#default-s3-buckets-production').trimmed();

    if(!(key && secret) && (staging || production)) {
        return 'You must enter keys to specify default staging and production buckets';
    }

    $.extend(cfg, {
        default_s3_access_key_id: key,
        default_s3_secret_access_key: secret,
        default_s3_buckets: {
            staging: staging,
            production: production
        }
    });
}

// Get and validate S3 credentials
function get_s3_credentials(cfg) {
    var error = '';
    var data = {};
    var has_defaults = cfg.default_s3_access_key_id && cfg.default_s3_secret_access_key;

    $('#s3').find('.bucket-group').not('.disabled').each(function(i, el) {
        var $el = $(el);
        var url = $el.find('.bucket-url').trimmed();
        var key = $el.find('.bucket-key').trimmed();
        var secret = $el.find('.bucket-secret').trimmed();

        if(url) {
            if(key && secret) {         // entered both
                data[url] = {
                    access_key_id: key,
                    secret_access_key: secret
                };
            } else if(key || secret) {  // entered only one
                if(has_defaults) {
                    error = 'You must enter an access key ID and a secret access key for each bucket (or leave both blank to use defaults)';
                } else {
                    error = 'You must enter an access key ID and a secret access key for each bucket';                
                }
            } else {                    // entered neither
                if(has_defaults) {
                    data[url] = {
                        access_key_id: settings.default_s3_access_key_id,
                        secret_access_key: settings.default_s3_secret_access_key
                    };
                } else {
                    error = 'You must enter an access key ID and a secret access key for each bucket';
                }
            }
        } else if(key || secret) {
            error = 'You must enter a name for each S3 bucket';
        }
        if(error) {
            return false;
        }
    });

    if(error) {
        return error;
    }

    $.extend(cfg.s3_credentials, data);
}

//
// Initialize controls in settings tab
//

function show_s3_credentials() {
    $('#s3_credentials').find('.bucket-group').remove();

    var $el = $('#s3_credentials').find('.bucket-add');
    for(var name in _config.s3_credentials) {
        bucket_add($el, $.extend({name: name}, _config.s3_credentials[name]), _add_bucket_template);
    }
    if(!Object.keys(_config.s3_credentials).length) {
        $el.click();
    }
}

function show_settings() {
    // Use Google?
    if(_settings.client_secrets) {
        $('#use_google').prop('checked', true);
        $('.google-secrets-exists').show();
        $('.google-secrets-needed').hide();
        $('.google_authenticate').enable();
    } else {
        $('#use_google').prop('checked', false);
        $('.google-secrets-exists').hide();
        $('.google-secrets-needed').show();
        $('.google_authenticate').disable();
    }

    // Google Emails
    $('#google_emails').enable().val(_config.google_account || '');

    // Use S3?
    if(_config.default_s3_access_key_id || _config.default_s3_secret_access_key) {
        $('#use_s3').prop('checked', true);
        $('#s3').addClass('in');
    } else {
        $('#use_s3').prop('checked', false);
        $('#s3').removeClass('in');
    }

    // S3 defaults
    $('#default-s3-access-key-id').val(_config.default_s3_access_key_id || '');
    $('#default-s3-secret-access-key').val(_config.default_s3_secret_access_key || '');
    $('#default-s3-buckets-staging').val(_config.default_s3_buckets.staging || '');
    $('#default-s3-buckets-production').val(_config.default_s3_buckets.production || '');

    // Additional S3 credentials
    show_s3_credentials();

    // Projects path
    $('#projects_path').val(_config.projects_path);
}

// Verify authorization code
function handle_google_auth_code($context, code) {
    $context.trigger('progress_show', 'Verifying code');

    ajax_get('/google/auth/code/', {code: code},
        function(error) {
          console.log("error");
            $context.trigger('error_show', error);
        },
        function(data) {
            console.log("data");
            $context.trigger('success_show', 'Authentication successful');
            show_settings();
        },
        function() {
          console.log("hiding progress");
            $context.trigger('progress_hide');
        });
}

// open authentication modal
function google_authenticate(){
  ajax_get('/google/auth/url/', {},
      function(error) {
          error_alert(error);
      },
      function(data) {
          input_show(_google_msg_template(data), function(yes, code) {
              if(yes) {
                  handle_google_auth_code($('settings_tab'), code);
              }
          });
      });
}

// Handle new client_secrets file selection
function handle_google_auth_secrets($context, file) {
     if(file) {
        var reader = new FileReader();
        reader.onerror = function() {
            $context.trigger('error_show', 'Error loading file');
        };

        reader.onload = function() {
            $context.trigger('progress_show', 'Copying file');

            ajax_post('/google/auth/secrets/', {content: reader.result},
                function(error) {
                    $context.trigger('error_show', 'Error copying file ('+error+')');
                },
                function(data) {
                    _settings = data.settings;
                    _config = _settings.config;
                    google_authenticate();
                },
                function() {
                    $context.trigger('progress_hide');
                });
        };

        $context.trigger('progress_show', 'Loading file');
        reader.readAsDataURL(file);
    }
}

$(function() {
    // Clear alerts/states when switching from tab to tab
    $('a[data-toggle="tab"]').on('hide.bs.tab', function(event) {
        alert_hide();
        $('.form-group, .input-group').removeClass('has-error');
    });

// ------------------------------------------------------------
// settings tab
// ------------------------------------------------------------

    var $settings_tab = $('#settings_tab')
        // mimic modal functions so we can re-use core routines
        .on('error_hide', error_hide)
        .on('error_show', function(event, msg) {
            error_alert(msg);
        })
        .on('progress_hide', progress_hide)
        .on('progress_show', function(event, msg) {
            progress_show(msg);
        })
        .on('success_show', function(event, msg) {
            success_alert(msg);
        })
        .on('change', 'input[type="text"]', settings_dirty)
        .on('change', 'textarea', settings_dirty)
        .on('click', 'input[type="checkbox"]', settings_dirty)
        .on('change', '#google_secrets_file', function(event) {
            handle_google_auth_secrets($settings_tab, event.target.files[0]);
        })
        .on('click', '.bucket-remove', function(event){
          event.preventDefault();
          bucket_remove(this);
        })
        .on('click', '.bucket-add', function(event){
          event.preventDefault();
          bucket_add(this);
        })
        .on('click', '.google_authenticate', function(event) {
            console.log("google_auth");
            google_authenticate();
        });

    // Save settings
    $('#settings_save').click(function(event) {
        var error = null;
        var data = $.extend(true, {}, _defaults);

        if($('#google_emails').val()) {
            data.google_account = $('#google_emails').trimmed();
        }

        //if($('#use_s3').is(':checked')) {
            //error = get_s3_defaults(data) || get_s3_credentials(data);
            //if(error) {
                //error_alert(error);
                //return;
            //}
        //}
        try {
          //get_s3_defaults(data);
          error = get_s3_defaults(data) || get_s3_credentials(data);
            if(error) {
                error_alert(error);
                return;
            }
          console.log("error", error);
        }
        catch(e) {
          console.log(e);
        }
        data.projects_path = $('#projects_path').val();

        progress_show('Saving configuration');

        ajax_post('/config/save/', {
                config: JSON.stringify(data)
            },
            function(error) {
                error_alert('Error saving settings ('+error+')');
            },
            function(unused) {
                _settings.config = data;
                _config = _settings.config;

                $('#settings_save').disable()
                success_alert('Settings saved!');

                show_s3_credentials();
            },
            function() {
                progress_hide();
            });
    });

// ------------------------------------------------------------
// Main
// ------------------------------------------------------------

    show_settings();

    $('#tab_content').show();
});
