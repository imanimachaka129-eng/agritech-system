function togglePassword(id){

    let password =
        document.getElementById(id);

    if(password.type === "password"){

        password.type = "text";

    }else{

        password.type = "password";

    }

}