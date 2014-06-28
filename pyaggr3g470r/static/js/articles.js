/*!
* pyAggr3g470r - A Web based news aggregator.
* Copyright (C) 2010-2014  Cédric Bonhomme - http://cedricbonhomme.org/
*
* For more information : https://bitbucket.org/cedricbonhomme/pyaggr3g470r/
*
* This program is free software: you can redistribute it and/or modify
* it under the terms of the GNU Affero General Public License as
* published by the Free Software Foundation, either version 3 of the
* License, or (at your option) any later version.
*
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
* GNU Affero General Public License for more details.
*
* You should have received a copy of the GNU Affero General Public License
* along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

if (typeof jQuery === 'undefined') { throw new Error('Requires jQuery') }

+function ($) {

    // Like or unlike an article
    $('.like').on('click', function() {
        var article_id = $(this).parent().parent().parent().attr("data-article");

        var data;
        if ($(this).hasClass("glyphicon-star")) {
            data = JSON.stringify({
                like: false
                })
                $(this).removeClass('glyphicon-star').addClass('glyphicon-star-empty');
        }
        else {
            data = JSON.stringify({
                like: true
                })
            $(this).removeClass('glyphicon-star-empty').addClass('glyphicon-star');
        }

        // sends the updates to the server
        $.ajax({
            type: 'PUT',
            // Provide correct Content-Type, so that Flask will know how to process it.
            contentType: 'application/json',
            // Encode your data as JSON.
            data: data,
            // This is the type of data you're expecting back from the server.
            url: "/api/v1.0/articles/"+article_id,
            success: function (result) {
                //console.log(result);
            },
            error: function(XMLHttpRequest, textStatus, errorThrown){
                console.log(XMLHttpRequest.responseText);
            }
        });
    });

    // Delete an article
    $('.delete').on('click', function() {
        var article_id = $(this).parent().parent().parent().attr("data-article");
        $(this).parent().parent().parent().remove();

         // sends the updates to the server
        $.ajax({
            type: 'DELETE',
            url: "/api/v1.0/articles/"+article_id,
            success: function (result) {
                //console.log(result);
            },
            error: function(XMLHttpRequest, textStatus, errorThrown){
                console.log(XMLHttpRequest.responseText);
            }
        });
    });

}(jQuery);
