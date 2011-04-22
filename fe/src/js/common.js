function collect_form_data(form_id) {
    return $(form_id).toQueryString().parseQueryString();
};

function csv2array(csv_str) {
    return csv_str.split(',').map(function(item, idx) {
        return item.trim()
    });
};

function popup_login(prev_req) {
    var login_form = $('relogin_form');
    var msgbox = $('relogin_msg');
    login_form.MooDialog();
    
    var request = new JSONRequest({
        url: '/login',
        onRequest: function(){
            msgbox.set('text', 'Logging in ...');
        },
        on_success: function(result, responseText) {
            var cur_uri = new URI();
            cur_uri.set('directory', '');
            cur_uri.set('file', result);
            cur_uri.go();
        },
        on_fail: function(result) {
            msgbox.set('text', "Try again..");
        }
    });

    $('re_login').addEvent('click', function(e) {
        request.postform('relogin_form');
    });
};

var JSONRequest = new Class ({
    Extends: Request.JSON,
    initialize: function(options){
        //options['Content-Type'] = 'application/json';
        options['urlEncoded'] = false;
        this.on_success = options['on_success'];
        this.on_fail = options['on_fail'];
        this.parent(options);
    },
    onSuccess: function(responseJSON, responseText) {
        var retcode = responseJSON['retcode'];
        var result = responseJSON['result'];
        // console.log(responseJSON);
        // console.log(result);
        if ((retcode == 0) && (this.success != null)) {
            this.on_success(result, responseText);
        } else if (retcode == 2) {
            if (this.on_fail != null) {
                this.on_fail(result);
            } else {
                popup_login(this);
            };
        } else if (retcode != 0) {
            if (this.on_fail != null) {
                this.on_fail(result);
            };
        };
    },
    json_send: function(data) {
        // console.log(data);
        // console.log(JSON.encode(data));
        this.setHeader('Content-Type', 'application/json');
        if (data) {
            this.send(JSON.encode(data));
        } else {
            this.send(options={method: 'get'});
        };
    },
});
