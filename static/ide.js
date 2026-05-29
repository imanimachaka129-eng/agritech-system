function togglePassword() {

    let password =
        document.getElementById("password");

    if (password.type === "password") {

        password.type = "text";

    } else {

        password.type = "password";

    }

}

function toggleConfirmPassword() {

    let confirmPassword =
        document.getElementById("confirm_password");

    if (confirmPassword.type === "password") {

        confirmPassword.type = "text";

    } else {

        confirmPassword.type = "password";

    }

}

