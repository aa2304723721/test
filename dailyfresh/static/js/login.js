$.ajax({
    url: "/xxx/StartCaptchaServlet?t=" + (new Date()).getTime(), // 加随机数防止缓存
    type: "get",
    dataType: "json",
    success: function (data) {
      console.log(data);
      alert('111'); //我这样是为了调试看看接口成功与否。成功则会弹出111
      // 调用 initGeetest 初始化参数
      // 参数1：配置参数
      // 参数2：回调，回调的第一个参数验证码对象，之后可以使用它调用相应的接口
      initGeetest({
        gt: data.gt,
        challenge: data.challenge,
        new_captcha: data.new_captcha, // 用于宕机时表示是新验证码的宕机
        offline: !data.success, // 表示用户后台检测极验服务器是否宕机，一般不需要关注
        product: "popup", // 产品形式，包括：float，popup
        width: "100%"
        // 更多配置参数请参见：http://www.geetest.com/install/sections/idx-client-sdk.html#config
      }, handler1);
    }
  });//滑动验证码
var handler1=function (captchaObj) {
   alert('222');//同样也是为了测试是否调用。//我这个项目是将该事件添加到了获取手机验证码上。s所以这个click的事件就写在获取手机验证码的按钮上。//就是你想把这个添加到哪个上面，你点击的就写哪个按钮
  $("#getphotocodeCode1").click(function () {
    var result = captchaObj.getValidate();
    if (!result) {
      $("#notice1").show();
      setTimeout(function () {
        $("#notice1").hide();
      }, 2000);
    }else{
     //这个地方写一些需要做的操作。比如我的项目，是在获取手机验证码之前需要判断手机号、密码等，那么这么判断就写在这里
      var mytimestamp = new Date().getTime();
      /*sendRanVerifiCode 发送手机/邮箱验证码*/
      var myajax=$.ajax({
        type: "post",
        url: "/xxx/xxx.do",
        timeout:15000,       //记住加上以下三个参数
        data :'"&geetest_challenge=" + result.geetest_challenge+"&geetest_validate="+result.geetest_validate+"&geetest_seccode="+result.geetest_seccode',
        //data:'',
        dataType: "json",
        "contentType": "application/x-www-form-urlencoded; charset=utf-8",
        success: function(data) {
          if (data.code=='success') {
            jybtools.showmsg("发送成功");
          }else{
            jybtools.showmsg(data.msg,1);
          }
        },
        complete : function(XMLHttpRequest, Status) {
          if(Status!='success'){//超时,status还有success,error等值的情况
            myajax.abort(); //取消请求
            console.log(Status);
          }else{
          }
        }
      });
    }
    e.preventDefault();
  })
  // 将验证码加到id为captcha的元素里，同时会有三个input的值用于表单提交
//  captchaObj.bindOn("#getphotocodeCode1");
  captchaObj.appendTo("#captcha1");
  captchaObj.onReady(function () {
    $("#wait1").hide();
  });
}