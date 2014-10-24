/**
 * Created by nicholasdrane on 10/22/14.
 */

var $ = jQuery;

var get_cities = function () {
    'use strict';
    var cities = retrieve_from_local('cities', true);
    if (!cities) {
        cities = $.get(window.additional_parameters.cities_list_url, function (data) {
            store_in_local('cities', data, true);
            cities = data;
        });
    }
    return cities;
};