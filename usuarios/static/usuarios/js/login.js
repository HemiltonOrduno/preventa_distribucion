/*===== FOCUS =====*/
const inputs = document.querySelectorAll(".form__input")

function addfocus(){
    let parent = this.parentNode.parentNode
    parent.classList.add("focus")
}

function remfocus(){
    let parent = this.parentNode.parentNode
    if(this.value == ""){
        parent.classList.remove("focus")
    }
}

inputs.forEach(input=>{
    input.addEventListener("focus",addfocus)
    input.addEventListener("blur",remfocus)
})

/*===== LOGIN =====*/
function getCookie(name) {
    const match = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)')
    return match ? match.pop() : ''
}

document.getElementById('loginForm').addEventListener('submit', async function(e){
    e.preventDefault()

    const usuario = document.getElementById('user').value
    const contrasena = document.getElementById('pass').value
    const errorMsg = document.getElementById('errorMsg')

    if (usuario === "" || contrasena === ""){
        errorMsg.textContent = "Completa ambos campos"
        return
    }
    errorMsg.textContent = ""

    try {
        const res = await fetch('/api/usuarios/login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ usuario, contrasena })
        })
        const data = await res.json()

        if (!res.ok){
            errorMsg.textContent = data.detail || "Error al iniciar sesión"
            return
        }
        window.location.href = data.redirect_url
    } catch (err) {
        errorMsg.textContent = "No se pudo conectar con el servidor"
    }
})