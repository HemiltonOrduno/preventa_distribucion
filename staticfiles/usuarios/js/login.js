/*===== FOCUS =====*/
const inputs = document.querySelectorAll(".form__input")

/*=== Add focus ===*/
function addfocus(){
    let parent = this.parentNode.parentNode
    parent.classList.add("focus")
}

/*=== Remove focus ===*/
function remfocus(){
    let parent = this.parentNode.parentNode
    if(this.value == ""){
        parent.classList.remove("focus")
    }
}

/*=== To call function ===*/
inputs.forEach(input=>{
    input.addEventListener("focus",addfocus)
    input.addEventListener("blur",remfocus)
})

/*===== LOGIN SUBMIT (placeholder, sin backend aún) =====*/
document.getElementById('loginForm').addEventListener('submit', function(e){
    e.preventDefault()

    const usuario = document.getElementById('user').value
    const contraseña = document.getElementById('pass').value
    const errorMsg = document.getElementById('errorMsg')

    if(usuario === "" || contraseña === ""){
        errorMsg.textContent = "Completa ambos campos"
        return
    }

    errorMsg.textContent = ""
    // aquí después conectamos el fetch al backend
})