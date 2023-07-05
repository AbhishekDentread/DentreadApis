function ajaxCall() {
    this.send = function(data, url, method, success, type) {
        type = 'json';
        var successRes = function(data) {
            success(data);
        }

        var errorRes = function(xhr, ajaxOptions, thrownError) {
            console.log(thrownError + "\r\n" + xhr.statusText + "\r\n" + xhr.responseText);
        }
        jQuery.ajax({
            url: url,
            type: method,
            data: data,
            success: successRes,
            error: errorRes,
            dataType: type,
            timeout: 60000
        });

    }
}

function locationInfo() {
    var rootUrl = "https://geodata.phplift.net/api/index.php";
    var call = new ajaxCall();
    this.getCities = function(id) {
        jQuery(".cities option:gt(0)").remove();

        var url = rootUrl + '?type=getCities&countryId=&stateId=' + id;
        var method = "post";
        var data = {};
        jQuery('.cities').find("option:eq(0)").html("Please wait..");
        call.send(data, url, method, function(data) {
            jQuery('.cities').find("option:eq(0)").html("Select City");
            var listlen = Object.keys(data['result']).length;

            if (listlen > 0) {
                jQuery.each(data['result'], function(key, val) {
                    var option = jQuery('<option />');
                    option.attr('value', val.name).text(val.name);
                    jQuery('.cities').append(option);
                });
            }

            jQuery(".cities").prop("disabled", false);
        });
    };

    this.getStates = function(id) {
        jQuery(".states option:gt(0)").remove();
        jQuery(".cities option:gt(0)").remove();

        var url = rootUrl + '?type=getStates&countryId=' + id;
        var method = "post";
        var data = {};
        jQuery('.states').find("option:eq(0)").html("Please wait..");
        call.send(data, url, method, function(data) {
            jQuery('.states').find("option:eq(0)").html("Select State");

            jQuery.each(data['result'], function(key, val) {
                var option = jQuery('<option />');
                option.attr('value', val.name).text(val.name);
                option.attr('stateid', val.id);
                jQuery('.states').append(option);
            });
            jQuery(".states").prop("disabled", false);
        });
    };

    this.getCountries = function() {
        var url = rootUrl + '?type=getCountries';
        var method = "post";
        var data = {};
        jQuery('.countries').find("option:eq(0)").html("Please wait..");
        call.send(data, url, method, function(data) {
            jQuery('.countries').find("option:eq(0)").html("Select Country");

            jQuery.each(data['result'], function(key, val) {
                var option = jQuery('<option />');

                option.attr('value', val.name).text(val.name);
                option.attr('countryid', val.id);

                jQuery('.countries').append(option);
            });

        });
    };

}

jQuery(function() {
    var loc = new locationInfo();
    loc.getCountries();

    // Attach change event handler to the country dropdown
    jQuery(".countries").on("change", function(ev) {
        var countryId = jQuery("option:selected", this).attr('countryid');
        if (countryId != '') {
            loc.getStates(countryId);
        } else {
            jQuery(".states option:gt(0)").remove();
        }

        // Reset the city dropdown
        jQuery(".cities option:gt(0)").remove();
        jQuery(".cities").prop("disabled", true);
        jQuery(".select-city-placeholder").show();
    });

    // Attach change event handler to the state dropdown
    jQuery(".states").on("change", function(ev) {
        var stateId = jQuery("option:selected", this).attr('stateid');
        if (stateId != '') {
            loc.getCities(stateId);
        } else {
            jQuery(".cities option:gt(0)").remove();
        }
    });
});