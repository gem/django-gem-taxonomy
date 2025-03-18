function validate_string(obj)
{
    tax_in = $($(obj).find('input[name="validate_input"]')[0]).val();
    $.ajax({
        url: "taxonomy/api/v1/validation/" + tax_in
    }).done(function(data) {
        $('div[name="validate_output"]').empty();
        if (data['success'] == true && data['is_canonical'] == true) {
            $('div[name="validate_output"]').append('<p style="font-weight: bold;">Result: <span style="color: green;">&#x2B24;</span></p><p>Input: ' + tax_in + '</p><p>Validation: Success</p><p>Canonical Form: True</p>');
        }
        else if (data['success'] == true && data['is_canonical'] == false) {
            $('div[name="validate_output"]').append('<p style="font-weight: bold;">Result: <span style="color: orange;">&#x2B24;</span></p><p>Input: ' + tax_in + '</p><p>Validation: Success</p><p>Is Canonical: False</p><p>Canonical form:' + data['canonical']);
        }
    }).fail(function(data) {
        $('div[name="validate_output"]').empty();
        $('div[name="validate_output"]').append('<p style="font-weight: bold;">Result: <span style="color: red;">&#x2B24;</span></p><p>Input: ' + tax_in + '</p><p>Validation: Failed</p><p>Message: ' + data.responseJSON['message'] + '</p>');
    })
}

// $('input[name=\'validate_input\']).val(\'\')
