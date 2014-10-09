var FormEditable = function () {

    //$.mockjaxSettings.responseTime = 500;

    var log = function (settings, response) {
        var s = [],
            str;
        s.push(settings.type.toUpperCase() + ' url = "' + settings.url + '"');
        for (var a in settings.data) {
            if (settings.data[a] && typeof settings.data[a] === 'object') {
                str = [];
                for (var j in settings.data[a]) {
                    str.push(j + ': "' + settings.data[a][j] + '"');
                }
                str = '{ ' + str.join(', ') + ' }';
            } else {
                str = '"' + settings.data[a] + '"';
            }
            s.push(a + ' = ' + str);
        }
        s.push('RESPONSE: status = ' + response.status);

        if (response.responseText) {
            if ($.isArray(response.responseText)) {
                s.push('[');
                $.each(response.responseText, function (i, v) {
                    s.push('{value: ' + v.value + ', text: "' + v.text + '"}');
                });
                s.push(']');
            } else {
                s.push($.trim(response.responseText));
            }
        }
        s.push('--------------------------------------\n');
        $('#console').val(s.join('\n') + $('#console').val());
    }

    var initEditables = function () {

        //set editable mode based on URL parameter
        if (App.getURLParameter('mode') == 'inline') {
            $.fn.editable.defaults.mode = 'inline';
            $('#inline').attr("checked", true);
            jQuery.uniform.update('#inline');
        } else {
            $('#inline').attr("checked", false);
            jQuery.uniform.update('#inline');
        }

        //global settings 
        $.fn.editable.defaults.inputclass = 'm-wrap';
        $.fn.editable.defaults.url = '/post';
        $.fn.editableform.buttons = '<button type="submit" class="btn blue editable-submit"><i class="icon-ok"></i></button>';
        $.fn.editableform.buttons += '<button type="button" class="btn editable-cancel"><i class="icon-remove"></i></button>';

        //editables element samples 
        $('.order').editable({
            url: "/admin/app_advertising/order/update",
            type: 'text',
            pk: $(this).attr("data-pk"),
            //name: "order",
            title: 'Enter order',
            validate: function (value) {
                if ($.trim(value) == '') return 'This field is required';
            }
        });

        $('.apptopic').editable({
            url: "/admin/app_topic/order/update",
            type: 'text',
            pk: $(this).attr("data-pk"),
            //name: "order",
            title: 'Enter order',
            validate: function (value) {
                if ($.trim(value) == '') return 'This field is required';
            }
        });

    }

    return {
        //main function to initiate the module
        init: function () {

            // init editable elements
            initEditables();


            // init editable toggler
            $('#enable').click(function () {
                $('#user .editable').editable('toggleDisabled');
            });

            // init 
            $('#inline').on('change', function (e) {
                if ($(this).is(':checked')) {
                    window.location.href = 'form_editable.html?mode=inline';
                } else {
                    window.location.href = 'form_editable.html';
                }
            });

            // handle editable elements on hidden event fired
            $('#user .editable').on('hidden', function (e, reason) {
                if (reason === 'save' || reason === 'nochange') {
                    var $next = $(this).closest('tr').next().find('.editable');
                    if ($('#autoopen').is(':checked')) {
                        setTimeout(function () {
                            $next.editable('show');
                        }, 300);
                    } else {
                        $next.focus();
                    }
                }
            });


        }

    };

}();