"use strict";

$(document).ready(function(){
    document.getElementById("copyButton").addEventListener("click", function() {
        copyToClipboard(document.getElementById("copyTarget"));
        $('#copyTarget').css({'background': '#9E9E9E'})

    });
    function copyToClipboard(elem) {
      // create hidden text element, if it doesn't already exist
        var targetId = "_hiddenCopyText_";
        var isInput = elem.tagName === "INPUT" || elem.tagName === "TEXTAREA";
        var origSelectionStart, origSelectionEnd;
        if (isInput) {
            // can just use the original source element for the selection and copy
            target = elem;
            origSelectionStart = elem.selectionStart;
            origSelectionEnd = elem.selectionEnd;
        } else {
            // must use a temporary form element for the selection and copy
            target = document.getElementById(targetId);
            if (!target) {
                var target = document.createElement("textarea");
                target.style.position = "absolute";
                target.style.left = "-9999px";
                target.style.top = "0";
                target.id = targetId;
                document.body.appendChild(target);
            }
            target.textContent = elem.textContent;
        }
        // select the content
        var currentFocus = document.activeElement;
        target.focus();
        target.setSelectionRange(0, target.value.length);
        
        // copy the selection
        var succeed;
        try {
              succeed = document.execCommand("copy");
        } catch(e) {
            succeed = false;
        }
        // restore original focus
        if (currentFocus && typeof currentFocus.focus === "function") {
            currentFocus.focus();
        }
        
        if (isInput) {
            // restore prior selection
            elem.setSelectionRange(origSelectionStart, origSelectionEnd);
        } else {
            // clear temporary content
            target.textContent = "";
        }
        return succeed;
    }
    $('#load-customer').on('input propertychange',function(){
        $.ajax({
            url: "/admin/customer/load-customer",
            data: {
                id: $('#load-customer').val()
            },
            type: "POST",
            beforeSend: function() {
                
            },
            error: function(data) {
                
            },
            success: function(data) {
                $('#show-load-customer').html(data);
                $('#show-load-customer').show();
               
                $('#show-load-customer li').on('click',function(){
                    $('#load-customer').val($(this).data('username'));
                    $('#p_node_append').val($(this).data('id'));
                    $('#show-load-customer').hide();
                })
            }
        });
    })

    $('#load-customer-position').on('input propertychange',function(){
        $.ajax({
            url: "/admin/customer/load-customer-position",
            data: {
                id: $('#load-customer-position').val()
            },
            type: "POST",
            beforeSend: function() {
                
            },
            error: function(data) {
                
            },
            success: function(data) {
                $('#show-load-customer-position').html(data);
                $('#show-load-customer-position').show();
               
                $('#show-load-customer-position li').on('click',function(){
                    $('#load-customer-position').val($(this).data('username'));
                    $('#p_binary_append').val($(this).data('id'));
                    $('#show-load-customer-position').hide();

                    if (parseInt($(this).data('position')) == 0)
                    {
                        $('#position').html('<option value="1">Bên trái</option><option value="2">Bên phải</option>')
                    }

                    if (parseInt($(this).data('position')) == 1)
                    {
                        $('#position').html('<option value="1">Bên trái</option>')
                    }
                    if (parseInt($(this).data('position')) == 2)
                    {
                        $('#position').html('<option value="2">Bên phải</option>')
                    }

                })
            }
        });
    })


    $('#verify').click(function(){
            if($(this).is(':checked')){
                document.getElementById("submitRegister").disabled = false;
            } else {
                document.getElementById("submitRegister").disabled = true; 
            }
        });


    $('.active_account_id').on('click',function(){
        //alert($(this).data('id'));
        $('#modalActiveCode #username_account').html($(this).data('username'));
        $('#modalActiveCode #customer_id').val($(this).data('id'));
        
        $('#modalActiveCode').modal('show');
    })

    $('#modalActiveCode #btnActiveCode').click(function(evt) {
        $.ajax({
            url: "/account/activecode",
            data: {
                code: $('#modalActiveCode #code').val(),
                customer_id: $('#modalActiveCode #customer_id').val()
            },
            type: "POST",
            beforeSend: function() {
                $('.btnConfirm').button('loading');
            },
            error: function(data) {
                $('.btnConfirm').button('reset');
            },
            success: function(data) {
                $('.btnConfirm').button('reset');
                var data = $.parseJSON(data);
                data.status == 'error' ? (
                    showNotification('top', 'right', data.message, 'danger')
                ) : (
                    showNotification('top', 'right', data.message, 'success')
                    
                   //setTimeout(function() {location.reload(true)}, 3)
                )
            }
        });

    });
});

function showNotification(from, align, msg, type) {
        /* type = ['','info','success','warning','danger','rose','primary'];*/
        var color = Math.floor((Math.random() * 6) + 1);
        $.notify({
            icon: "notifications",
            message: msg
        }, {
            type: type,
            timer: 3000,
            placement: {
                from: from,
                align: align
            }
        });
    }
$('#submitLogin').click(function(){
    $('form#frmLogin').submit();
    $('#submitLogin').hide();
})
$('#submitRegister').click(function(){
    $('form#frmRegister').submit();
    $('#submitRegister').hide();
})

$('#submitReset').click(function(){
    $('form#frmReset').submit();
    $('#submitReset').hide();
})