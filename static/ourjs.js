function post() {
    let comment = $('#textarea-post').val();
    let today = new Date().toISOString();
    $.ajax({
        type: 'POST',
        url: '/posting',
        data: {
            'comment_give': comment,
            'date_give': today,
        },
        success: function (response) {
            $('#modal-post').removeClass('is-active');
            window.location.reload();
        },
    });
};

function num2str(count){
    if(count>10000){
        return parseInt(count/1000)+'k';
    };
    if(count>500){
        // 1000 menjadi 100 menjadi 1+k
        // 550 menjadi 5 menjadi 0.5+k
        return parseInt(count/100)/10+'k';
    };
    if(count == 0){
        return '';
    };
    return count;
};

function toggle_like(id,type){
    let $A_like = $(`#${id} a[aria-label='heart']`);
    let $I_like = $A_like.find('i');
    if ($I_like.hasClass('fa-solid')){
        $.ajax({
            type:'POST',
            url:'/update_like',
            data:{
                'post_id_give':id,
                'type_give':type,
                'action_give':'unlike'
            },
            success:function(response){
                $I_like.addClass('fa-regular').removeClass('fa-solid');
                $A_like.find('span.like-num').text(num2str(response['count']));
            },
        });
    } else {
        $.ajax({
            type:'POST',
            url:'/update_like',
            data:{
                'post_id_give':id,
                'type_give':type,
                'action_give':'like'
            },
            success:function(response){
                $I_like.addClass('fa-solid').removeClass('fa-regular');
                $A_like.find('span.like-num').text(num2str(response['count']));
            },
        });
    };
};

function toggle_thumbs_up(id,type){
    let $A_like = $(`#${id} a[aria-label='thumbs_up']`);
    let $I_like = $A_like.find('i');
    if ($I_like.hasClass('fa-solid')){
        $.ajax({
            type:'POST',
            url:'/update_like',
            data:{
                'post_id_give':id,
                'type_give':type,
                'action_give':'unlike'
            },
            success:function(response){
                $I_like.addClass('fa-regular').removeClass('fa-solid');
                $A_like.find('span.like-num').text(num2str(response['count']));
            },
        });
    } else {
        $.ajax({
            type:'POST',
            url:'/update_like',
            data:{
                'post_id_give':id,
                'type_give':type,
                'action_give':'like'
            },
            success:function(response){
                $I_like.addClass('fa-solid').removeClass('fa-regular');
                $A_like.find('span.like-num').text(num2str(response['count']));
            },
        });
    };
};

function toggle_star(id,type){
    let $A_like = $(`#${id} a[aria-label='star']`);
    let $I_like = $A_like.find('i');
    if ($I_like.hasClass('fa-solid')){
        $.ajax({
            type:'POST',
            url:'/update_like',
            data:{
                'post_id_give':id,
                'type_give':type,
                'action_give':'unlike'
            },
            success:function(response){
                $I_like.addClass('fa-regular').removeClass('fa-solid');
                $A_like.find('span.like-num').text(num2str(response['count']));
            },
        });
    } else {
        $.ajax({
            type:'POST',
            url:'/update_like',
            data:{
                'post_id_give':id,
                'type_give':type,
                'action_give':'like'
            },
            success:function(response){
                $I_like.addClass('fa-solid').removeClass('fa-regular');
                $A_like.find('span.like-num').text(num2str(response['count']));
            },
        });
    };
};
function time_to_string(input_time){
    let today = new Date();
    let time = (today - input_time) / 1000 / 60;
    if (time < 60){
        return parseInt(time)+' minutes ago';
    }
    time = time / 60;
    if (time < 24){
        return parseInt(time)+' hours ago';
    }
    time = time / 24;
    if (time < 7){
        return parseInt(time)+' days ago';
    }
    let months = ["January","February","March","April","May","June","July","August","September","October","November","December"];
    let year = input_time.getFullYear();
    let month = months[input_time.getMonth()]; //Get month mengembalikan index
    let day = input_time.getDate();
    return `${day} ${month}, ${year}`;
};
function get_posts(username) {
    if (username == undefined){username = ''};
    $('#post-box').empty();
    $.ajax({
        type: 'GET',
        url: `/get_posts?username_give=${username}`,
        data: {},
        success: function (response) {
            if (response['result'] == 'success') {
                let posts = response['posts'];
                for (let i = 0; i < posts.length; i++) {
                    let post = posts[i];
                    let time_post = new Date(post['date']);
                    let heart_class = post['heart_by_me'] ? 'fa-solid':'fa-regular';
                    let star_class = post['star_by_me'] ? 'fa-solid':'fa-regular';
                    let thumbs_up_class = post['thumbs_up_by_me'] ? 'fa-solid':'fa-regular';
                    let html_temp = `
                    <div class="box" id="${post['_id']}">
                        <article class="media">
                            <div class="media-left">
                                <a class="image is-64x64" href="/user/${post['username']}">
                                    <img class="is-rounded"
                                        src="/static/${post['profile_pic_real']}"
                                        alt="image"/>
                                </a>
                            </div>
                            <div class="media-content">
                                <div class="content">
                                    <p>
                                        <strong>${post['profile_name']}</strong><small> @${post['username']}</small>
                                        <small>${time_to_string(time_post)}</small>
                                        <br>
                                        ${post['comment']}
                                    </p>
                                </div>
                                <nav class="level is-mobile">
                                    <div class="level-left">
                                        <a class="level-item is-fox" aria-label="heart" onclick="toggle_like('${post["_id"]}','heart')">
                                            <span class="icon is-small">
                                                <i class="fa fa-heart ${heart_class}" area-hidden="true"></i>
                                            </span>&nbsp;<span class="like-num">${num2str(post['count_heart'])}</span>
                                        </a>
                                        <a class="level-item is-fox" aria-label="star" onclick="toggle_star('${post["_id"]}','star')">
                                            <span class="icon is-small">
                                                <i class="fa fa-star ${star_class}" area-hidden="true"></i>
                                            </span>&nbsp;<span class="like-num">${num2str(post['count_star'])}</span>
                                        </a>
                                        <a class="level-item is-fox" aria-label="thumbs_up" onclick="toggle_thumbs_up('${post["_id"]}','thumbs_up')">
                                            <span class="icon is-small">
                                                <i class="fa fa-thumbs-up ${thumbs_up_class}" area-hidden="true"></i>
                                            </span>&nbsp;<span class="like-num">${num2str(post['count_thumbs_up'])}</span>
                                        </a>
                                    </div>
                                </nav>
                            </div>
                        </article>
                    </div>`;
                    $('#post-box').append(html_temp);
                };
            };
        },
    });
};