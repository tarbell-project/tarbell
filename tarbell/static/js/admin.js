// admin.js, admin GUI functions
// required jquery, json2

//
// templates
//

var _error_alert_template = _.template($('#error_alert_template').html());
var _success_alert_template = _.template($('#success_alert_template').html());

var _project_template = _.template($('#project_template').html());
var _blueprint_template = _.template($('#blueprint_template').html());

var _google_msg_template = _.template($('#google_msg_template').html());
var _bucket_template = _.template($('#bucket_template').html());

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
        .on('click', '.btn-default', function(event) {
            $input_modal.modal('hide');
            callback(false);
        })
        .on('click', '.btn-primary', function(event) {
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

// Disable row of S3 bucket controls
function bucket_disable(target) {
    var $group = $(target).closest('.form-group');
    $group.find('input').disable();
    $group.find('.bucket-disable').hide();
    $group.find('.bucket-enable').show();
    settings_dirty();
}

// Enable row of S3 bucket controls
function bucket_enable(target) {
    var $group = $(target).closest('.form-group');
    $group.find('input').enable();
    $group.find('.bucket-enable').hide();
    $group.find('.bucket-disable').show();
}

// Remove set of S3 bucket controls
function bucket_remove(target) {
    $(target).closest('.form-group').remove();
}

// Add row of S3 bucket controls
function bucket_add(target, data) {
    var d = $.extend(
        {name: '', access_key_id: '', secret_access_key: ''},
        data || {}
    );
    var $group = $(target).closest('.form-group');    
    $(_bucket_template(d)).insertBefore($group);
}

// Show google settings in controls in $scope
function show_google($scope, cfg) {
    if(_settings.client_secrets) {
        $scope.find('.google-secrets-exists').show();
        $scope.find('.google-authenticate').enable();
        $scope.find('.google-emails').enable().val(cfg.google_account || '');
        $scope.addClass('in');
    } else {
        $scope.find('.google-secrets-exists').hide();
        $scope.find('.google-authenticate').disable();
        $scope.find('.google-emails').disable().val(cfg.google_account || '');   
        $scope.removeClass('in');
    }
}

// Get and validate google settings from controls in $scope
function get_google($scope, cfg) {
    cfg.google_account = $scope.find('.google-emails').trimmed();
}

// Show S3 defaults in controls in $scope
function show_s3_defaults($scope, cfg) {
    $scope.find('.default-s3-access-key-id').val(cfg.default_s3_access_key_id || '');
    $scope.find('.default-s3-secret-access-key').val(cfg.default_s3_secret_access_key || '');
    $scope.find('.default-staging').val(cfg.default_s3_buckets.staging || '');
    $scope.find('.default-production').val(cfg.default_s3_buckets.production || '');
}

// Get and validate S3 defaults from controls in $scope
function get_s3_defaults($scope, cfg) {
    var key = $scope.find('.default-s3-access-key-id').trimmed();
    var secret = $scope.find('.default-s3-secret-access-key').trimmed();
    var staging = $scope.find('.default-staging').trimmed();
    var production = $scope.find('.default-production').trimmed();
    
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

// Show S3 credentials in controls in $scope
function show_s3_credentials($scope, cfg) {
    $scope.find('.bucket-group').remove();

    var $el = $scope.find('.bucket-add');
    
    for(var name in cfg.s3_credentials) {
        bucket_add($el, $.extend({name: name}, cfg.s3_credentials[name]));
    } 
    if(!Object.keys(cfg.s3_credentials).length) {
        $el.click();
    }
}

// Get and validate S3 credentials from controls in $scope
function get_s3_credentials($scope, cfg) {
    var error = '';
    var data = {};
    var has_defaults = cfg.default_s3_access_key_id && cfg.default_s3_secret_access_key;

    $scope.find('.bucket-group').each(function(i, el) {
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
                    error = 'You must enter an access key and a secret access key for each bucket (or leave both blank to use defaults)';
                } else {
                    error = 'You must enter an access key and a secret access key for each bucket';                
                }
            } else {                    // entered neither
                if(has_defaults) {  
                    data[url] = {
                        access_key_id: settings.default_s3_access_key_id,
                        secret_access_key: settings.default_s3_secret_access_key
                    };              
                } else {
                    error = 'You must enter an access key and a secret access key for each bucket';
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

// Initialize controls in settings tab
function show_settings() {        
    $('#use_google').prop('checked', _settings.client_secrets);
    show_google($('#google'), _config);
       
    if(_config.default_s3_access_key_id || _config.default_s3_secret_access_key) {
        $('#use_s3').prop('checked', true);
        $('#s3').addClass('in');    
    } else {
        $('#use_s3').prop('checked', false);
        $('#s3').removeClass('in');
    } 
        
    show_s3_defaults($('#s3'), _config);    
    show_s3_credentials($('#s3_credentials'), _config);    

    $('#projects_path').val(_config.projects_path);
}

function show_projects() {
    ajax_get('/projects/list/', {},
        function(error) {
            $('#projects_alert').hide();
            $('#projects_table').hide();
            error_alert('Error listing projects ('+error+')');
        },
        function(data) {    
            var projects = data.projects;    
            var html = '';
    
            for(var i = 0; i < projects.length; i++) {
                html += _project_template({d: projects[i]});
            }    
            if(projects.length) {
                $('#projects_alert').hide();
                $('#projects_table tbody').html(html);
                $('#projects_table').show();
            } else {
                $('#projects_alert').show();
                $('#projects_table').hide();        
            }
        });
}

function show_blueprints() {
    var blueprints = _settings.config.project_templates;
    var html = '';

    for(var i = 0; i < blueprints.length; i++) {
        html += _blueprint_template({d: blueprints[i]});
    }  
    if(blueprints.length) {
        $('#blueprints_alert').hide();
        $('#blueprints_table tbody').html(html);
        $('#blueprints_table').show();
    } else {
        $('#blueprints_alert').show();
        $('#blueprints_table').hide();        
    }
}

// Verify authorization code
function handle_google_auth_code($context, code) {
    $context.trigger('progress_show', 'Verifying code');
      
    ajax_get('/google/auth/code/', {code: code},
        function(error) {
            $context.trigger('error_show', error);
        },
        function(data) {
            $context.trigger('success_show', 'Authentication successful');               
        },
        function() {
            $context.trigger('progress_hide');
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
                    $('.google-authenticate, .google-emails').enable();
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
        .on('click', 'input[type="checkbox"]', settings_dirty)
        .on('change', '.google-secrets-file', function(event) {
            handle_google_auth_secrets($settings_tab, event.target.files[0]);
        })
        .on('click', '.google-authenticate', function(event) {
             ajax_get('/google/auth/url/', {},
                function(error) {
                    error_alert(error);
                },
                function(data) {
                    input_show(_google_msg_template(data), function(yes, code) {
                        if(yes) {
                            handle_google_auth_code($settings_tab, code);
                        }
                    });
                });                    
        });

    // Save settings
    $('#settings_save').click(function(event) {  
        var error = null;   
        var data = $.extend(true, {}, _defaults);

        if($('#use_google').is(':checked')) {
            error = get_google($('#google'), data);    
            if(error) {
                error_alert(error);
                return;
            }
        }
        
        if($('#use_s3').is(':checked')) {        
            error = get_s3_defaults($('#s3'), data)
                 || get_s3_credentials($('#s3'), data);               
            if(error) {
                error_alert(error);
                return;
            }
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
                
                show_projects();
                show_blueprints();
                
                $('#settings_save').disable()
                success_alert('Settings saved!');
            },
            function() {
                progress_hide();
            });
    });
 
// ------------------------------------------------------------
// config modal
// ------------------------------------------------------------
            
    var $config_modal = modal_init($('#config_modal'))
        .on('show.bs.modal', function(event) { 
            $config_modal.find('.config-panel').hide();                              
            $('#config_save').hide();
            $('#config_next').show();          
            $config_modal.trigger('show_welcome');
        })
        .on('show_panel', function(event, id) {
            $config_modal.trigger('all_hide')
                .find('.config-panel:visible').hide();
            $('#'+id).show();              
        })
        .on('show_welcome', function(event) {
            $('#config_next')
                .off('click.next')
                .on('click.next', function(event) {
                    $config_modal.trigger('show_google');
                });      
            
            $(this).trigger('show_panel', 'config_welcome_panel');
        })
        .on('show_google', function(event) {
            if(_settings.client_secrets) {
                $('input[name="config_google"][value="1"]').click();
            } else {
                $('input[name="config_google"][value=""]').click(); 
            }
            
            show_google($('#config_google_panel .config-collapse'), _config);
                                           
            $('#config_next')
                .off('click.next')
                .on('click.next', function(event) {
                    var error = null;
                    
                    error = get_google($('#config_google_panel'), _config);
                    if(error) {
                        $config_modal.trigger('error_show', error);
                    } else {           
                        $config_modal.trigger('show_s3');
                    }
                });      
            
            $(this).trigger('show_panel', 'config_google_panel');
        })
        .on('show_s3', function(event) {      
            var $scope = $('#config_s3_panel');
                 
            if(_config.default_s3_access_key_id
            || _config.default_s3_secret_access_key) {
                $scope.find('input[name="config_s3"][value="1"]').click(); 
            } else {
                $scope.find('input[name="config_s3"][value=""]').click(); 
            }
            
            show_s3_defaults($scope, _config);

            $('#config_next')
                .off('click.next')
                .on('click.next', function(event) {
                    var error = null;
                    
                    if($scope.find('input[name="config_s3"]:checked').val()) {
                        error = get_s3_defaults($scope, _config);
                        
                        if(error) {
                            $config_modal.trigger('error_show', error);
                        } else {                   
                            $config_modal.trigger('show_buckets');
                        }
                    } else {
                        $.extend(_config, {
                            default_s3_access_key_id: '',
                            default_s3_secret_access_key: '',
                            default_s3_buckets: {
                                staging: '',
                                production: ''
                            }
                        });
                    
                        $config_modal.trigger('show_path');
                    }
                });
                                        
            $(this).trigger('show_panel', 'config_s3_panel');
        })
        .on('show_buckets', function(event) {
            var $scope = $('#config_buckets_panel');
            
            show_s3_credentials($scope, _config);

            if(Object.keys(_config.s3_credentials).length) {
                $scope.find('input[name="config_buckets"][value="1"]').click(); 
            } else {
                $scope.find('input[name="config_buckets"][value=""]').click(); 
            }     

            $('#config_next')
                .off('click.next')
                .on('click.next', function(event) {
                    error = get_s3_credentials($('#config_buckets_panel'), _config);
 
                     if(error) {
                        $config_modal.trigger('error_show', error);
                        return;
                    }
                           
                    $config_modal.trigger('show_path');
                });
  
            $config_modal.trigger('show_panel', 'config_buckets_panel');      
       })
        .on('show_path', function(event) {        
            $('#config_projects_path').val(_config.projects_path);

            $('#config_next')
                .off('click.next')
                .hide();
            
            $('#config_save')
                .off('click.save')
                .on('click.save', function(event) {         
                    _config.projects_path = $('#config_projects_path').trimmed();
                                
                    ajax_post('/config/save/', {
                            config: JSON.stringify(_config)
                        },
                        function(error) {
                            $config_modal.trigger('error_show', 'Error saving settings ('+error+')');
                        },
                        function(data) {
                            show_projects();
                            show_blueprints();
                            show_settings();
                            $('#tab_content').show();
                            success_alert('Your settings have been saved and your Tarbell installation has been configured!');
                            $config_modal.modal('hide');
                        },
                        function() {
                            $config_modal.trigger('progress_hide');
                        });
                })
                .show();
          
            $(this).trigger('show_panel', 'config_path_panel'); 
        })
        // collapsables
        .on('click', 'input[name="config_google"], input[name="config_s3"], input[name="config_buckets"]', function(event) {
            var $el = $(this).closest('.config-panel').find('.config-collapse');
            if($(this).val()) {
                $el.show();
            } else {
                $el.hide();        
            }
        })
        // client_secrets
        .on('change', '.google-secrets-file', function(event) {
            handle_google_auth_secrets($config_modal, event.target.files[0]);
        })
        .on('click', '.google-authenticate', function(event) {
            ajax_get('/google/auth/url/', {},
                function(error) {
                    $config_modal.trigger('error_show', error);
                },
                function(data) {                    
                    $config_modal.trigger('input_show', [
                        _google_msg_template(data), 
                        function(yes, code) {
                            if(yes) {
                                handle_google_auth_code($config_modal, code);
                            }
                        }
                    ]);          
                });
        });        
    
// ------------------------------------------------------------
// run modal
// ------------------------------------------------------------

    var $run_modal = modal_init($('#run_modal'))
        .on('show.bs.modal', function(event) {
            $run_modal.trigger('all_hide');
            
            $(this).data('data-project', 
                $(event.relatedTarget).closest('tr').attr('data-project'));  
            
            $('#run_address').val('127.0.0.1:5000').enable();
            $('#run_done_button, #run_button').show();              
            $('#run_stop_button').hide();
        })
        .on('click', '#run_button', function(event) {   
            $run_modal.trigger('all_hide');
            
            var project = $run_modal.data('data-project');
           
            var $address = $('#run_address');
            var address = $address.val().trim();
            if(!address) {
                $address.focus().closest('.form-group').addClass('has-error');
                return;
            }
            $address.closest('.form-group').removeClass('has-error');
            
            $run_modal.trigger('progress_show', 'Starting preview server');
    
            ajax_get('/project/run/', {
                    project: project,
                    address: address
                }, 
                function(error) {
                    $run_modal.trigger('error_show', error);
                },
                function(data) {
                    if(data.warning) {
                        $run_modal.trigger('error_show', data.warning);
                    }
                    window.open('http://'+address);
            
                    $('#run_address').disable();
                    $('#run_done_button, #run_button').hide();   
                    $('#run_stop_button').show();
                },
                function() {
                    $run_modal.trigger('progress_hide');
                }
            );
        })
        .on('click', '#run_stop_button', function(event) {
            ajax_get('/project/stop/', {}, 
                function(error) {
                    $run_modal.trigger('error_show', error);
                },
                function(data) {
                    $('#run_address').enable();              
                    $('#run_stop_button').hide();
                    $('#run_done_button, #run_button').show();   
                }
            );
        });  

// ------------------------------------------------------------
// main
// ------------------------------------------------------------

    if(_settings.file_missing || window.location.search == '?configure') {
        $('#config_modal').modal('show');
    } else {
        show_projects();
        show_blueprints();
        show_settings();
        $('#tab_content').show();
    }
 
});