//This is needed because loading of JQuery takes time.
var menu_open=false;
var is_current_user_anonymous=1;

document.addEventListener("DOMContentLoaded", function(event) {
    $(function() {
        $('#hamburger_menu').click(function () {
            console.log('hambergur is good');
            current_user = $("#hidden_user_name").html();

            if (menu_open){
                console.log('menu is open and is user anonymous: ', is_current_user_anonymous)
                if (is_current_user_anonymous) {
                    str='<div class="login_text" id="login_text">' + '<a href="/login">Login</a></div>'
                    $("#greetings_panel").html(str);
                }else{
                    let str="<div class='greetings_text' id='greetings_text'> (Welcome )"+current_user+"</div>"
                    str+='<div class="login_text" id="login_text">' + '<a href="/logout">Logout</a></div>'
                    $("#greetings_panel").html(str);
                }
                $("#greetings_panel").show();
            }else{
                console.log('menu is closed and is user anonymous: ', is_current_user_anonymous)
                $("#greetings_panel").hide();
                if (is_current_user_anonymous) {
                    str='<div class="login_text" id="login_text">' + '<a href="/login">Login</a></div>'
                    $("#greetings_panel").html(str);
                }else{
                    let str="<div class='greetings_text' id='greetings_text'> (Welcome )"+current_user+"</div>"
                    str+='<div class="login_text" id="login_text">' + '<a href="/logout">Logout</a></div>'
                    $("#greetings_panel").html(str);
                }
            }
        });
        $("#position_date").on("change", function() {
            date_value = this.value
            $.ajax({
                url : "/review_positions",
                type: 'POST',
                contentType: 'application/json',
                dataType: 'json',
                data: JSON.stringify({
                    'date_value': date_value
                }),
                success: function(response){
                    table_html= response['tables'];
                    $("#table_panel").html(table_html);
                },
                error: function(error){
                    console.log('error: ', error)
                }
            });
        });

    });
});

function run_hamburger_menu(comp) {
    if (menu_open){
        menu_open=false;
    }else{
        menu_open=true
    }
    console.log('comp is going to display: ', comp);
    comp.classList.toggle("change");
}

