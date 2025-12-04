import re
import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .forms import ClienteRegistroForm, RegistroEmpresaForm
from .models import Usuario
from empresas.models import Empresa

# -------------------------
# LOGIN GLOBAL (tu código)
# -------------------------
def login_global(request):
    errors = {}
    if request.method == "POST":
        email = (request.POST.get("username") or "").strip()
        password = request.POST.get("password")
        role = request.POST.get("role")

        # ADMIN (usuario django)
        if role == "administrador":
            try:
                user_obj = User.objects.get(email=email)
            except User.DoesNotExist:
                errors["email"] = "No existe un administrador con este correo."
                return render(request, "core/login.html", {"errors": errors})

            user = authenticate(request, username=user_obj.username, password=password)
            if user is None:
                errors["password"] = "Contraseña incorrecta."
                return render(request, "core/login.html", {"errors": errors})

            if not user.is_superuser and not user.is_staff:
                errors["email"] = "Este usuario no tiene permisos de administrador."
                return render(request, "core/login.html", {"errors": errors})

            login(request, user)
            return redirect("administrador")

        # Otros roles -> tabla Usuario
        roles_dict = {"cliente": 1, "empresa": 2, "operador": 3}
        rol_id_esperado = roles_dict.get(role)

        try:
            usuario = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            errors["email"] = "El correo no está registrado."
            return render(request, "core/login.html", {"errors": errors})

        if usuario.rol_id != rol_id_esperado:
            errors["email"] = "Este usuario no pertenece al tipo seleccionado."
            return render(request, "core/login.html", {"errors": errors})

        if not check_password(password, usuario.password):
            errors["password"] = "La contraseña es incorrecta."
            return render(request, "core/login.html", {"errors": errors})

        # guardar sesión
        request.session["usuario_id"] = usuario.id_usuario
        request.session["usuario_nombre"] = usuario.nombre
        request.session["usuario_rol"] = usuario.rol_id

        if usuario.rol_id == 1:
            return redirect("cliente")
        elif usuario.rol_id == 2:
            return redirect("empresa")
        elif usuario.rol_id == 3:
            return redirect("operador")

    return render(request, "core/login.html")


# -------------------------
# REGISTROS (mantener como están)
# -------------------------
def registro_cliente(request):
    if request.method == 'POST':
        form = ClienteRegistroForm(request.POST)
        if form.is_valid():
            if Usuario.objects.filter(email=form.cleaned_data['email']).exists():
                form.add_error('email', "Este correo ya está registrado.")
                return render(request, 'core/registro_cliente.html', {'form': form})

            usuario = form.save(commit=False)
            usuario.password = make_password(form.cleaned_data['password'])
            usuario.rol_id = 1
            usuario.is_active = True
            usuario.save()
            messages.success(request, "Registro exitoso. Ahora puedes iniciar sesión.")
            return redirect("login")
    else:
        form = ClienteRegistroForm()
    return render(request, 'core/registro_cliente.html', {'form': form})


def registro_empresa(request):
    if request.method == "POST":
        nombre_rep = (request.POST.get("nombre_representante") or "").strip()
        email = (request.POST.get("email") or "").strip()
        telefono = (request.POST.get("telefono") or "").strip()
        password = request.POST.get("password") or ""
        password2 = request.POST.get("password2") or ""

        razon_social = (request.POST.get("razon_social") or "").strip()
        nit = (request.POST.get("nit") or "").strip()
        direccion = (request.POST.get("direccion") or "").strip()
        ciudad = (request.POST.get("ciudad") or "").strip()

        rut_file = request.FILES.get("rut")
        camara_file = request.FILES.get("camara_comercio")
        licencia_file = request.FILES.get("licencia_operacion")

        errores = []
        if password != password2:
            errores.append("Las contraseñas no coinciden")
        if Usuario.objects.filter(email=email).exists():
            errores.append("Email ya registrado")
        if Empresa.objects.filter(nit=nit).exists():
            errores.append("NIT ya registrado")

        if errores:
            for e in errores:
                messages.error(request, e)
            return render(request, "core/registro_empresa.html")

        try:
            usuario = Usuario.objects.create(
                nombre=nombre_rep,
                email=email,
                telefono=telefono,
                password=make_password(password),
                rol_id=2,
                is_active=False
            )
            empresa = Empresa.objects.create(
                id_usuario=usuario,
                nombre=razon_social,
                nit=nit,
                direccion=direccion,
                ciudad=ciudad,
                estado='pendiente',
                rut=rut_file,
                camara_comercio=camara_file,
                licencia_operacion=licencia_file,
            )
            messages.success(request, "Registro completado. Empresa pendiente de validación.")
            return redirect("login")
        except Exception as exc:
            messages.error(request, "Error interno al registrar la empresa")
            return render(request, "core/registro_empresa.html")

    return render(request, "core/registro_empresa.html")


def registro_operador(request):
    if request.method == "POST":
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        telefono = request.POST.get('telefono')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if password != password2:
            messages.error(request, "Las contraseñas no coinciden.")
            return redirect('registro_operador')

        if Usuario.objects.filter(email=email).exists():
            messages.error(request, "Este correo ya está registrado.")
            return redirect('registro_operador')

        Usuario.objects.create(
            nombre=nombre,
            email=email,
            telefono=telefono,
            password=make_password(password),
            rol_id=3,
            is_active=True
        )

        messages.success(request, "Operador registrado correctamente.")
        return redirect('login')

    return render(request, 'core/registro_operador.html')


# -------------------------
# LOGOUT, validar_email, cliente_view
# -------------------------
def logout_view(request):
    request.session.flush()
    return redirect("login")


def validar_email(request):
    email = request.GET.get("email")
    existe = Usuario.objects.filter(email=email).exists()
    return JsonResponse({"existe": existe})


def cliente_view(request):
    return render(request, "core/cliente.html")


# -------------------------
# PERFIL (unificado)
# -------------------------
def perfil(request):
    """
    Muestra el perfil del usuario logueado (según sesión).
    - Si es administrador (django auth) mostramos su perfil admin (si quieres).
    - Si es Usuario (tabla Usuario) mostramos plantilla por rol (operador -> operadores/perfil_operador.html)
    """
    # Si es admin autenticado con Django
    if request.user.is_authenticated and (getattr(request.user, "is_staff", False) or getattr(request.user, "is_superuser", False)):
        # puedes renderizar un template para admin si lo tienes
        return render(request, "usuarios/perfil_generico.html", {"django_user": request.user})

    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        messages.error(request, "Debes iniciar sesión.")
        return redirect("login")

    usuario = get_object_or_404(Usuario, id_usuario=usuario_id)

    # según rol, usar plantilla distinta
    if usuario.rol_id == 3:
        return render(request, "operadores/perfil_operador.html", {"operador": usuario})
    else:
        # plantilla genérica para cliente/empresa u otros
        return render(request, "usuarios/perfil_generico.html", {"usuario": usuario})

# --- RECUPERAR CONTRASEÑA POR CORREO DESDE EL LOGIN ---
# ------------------- RECUPERAR CONTRASEÑA DESDE LOGIN -------------------

def recuperar_contrasena_correo(request):
    """
    1) Si el correo pertenece a un admin Django → usa sistema nativo con tokens oficiales.
    2) Si pertenece a usuario normal → usa token UUID personalizado.
    """
    if request.method == "POST":
        correo = request.POST.get("email")

        # -------------------------
        # 1) ADMIN (auth_user)
        # -------------------------
        try:
            admin_user = User.objects.get(email=correo)

            uid = urlsafe_base64_encode(force_bytes(admin_user.pk))
            token = default_token_generator.make_token(admin_user)

            link = request.build_absolute_uri(
                reverse("password_reset_confirm", kwargs={"uidb64": uid, "token": token})
            )

            # usa tus plantillas EXISTENTES
            mensaje_txt = render_to_string("usuarios/password_reset_email.txt", {
                "user": admin_user,
                "reset_link": link,
            })

            mensaje_html = render_to_string("usuarios/password_reset_email_html.html", {
                "user": admin_user,
                "reset_link": link,
            })

            send_mail(
                subject="Recuperación de contraseña",
                message=mensaje_txt,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[correo],
                html_message=mensaje_html,
                fail_silently=False,
            )

            messages.success(request, "Se ha enviado un enlace de recuperación a tu correo.")
            return redirect("usuarios:login")

        except User.DoesNotExist:
            pass  # No es admin → seguimos con usuarios normales

        # -------------------------
        # 2) USUARIO NORMAL (tabla Usuario)
        # -------------------------
        usuario = Usuario.objects.filter(email=correo).first()

        if usuario:
            token = str(uuid.uuid4())
            usuario.token_recuperacion = token
            usuario.fecha_token = timezone.now()
            usuario.save()

            reset_url = reverse("usuarios:reset_password")
            link = request.build_absolute_uri(f"{reset_url}?token={token}")

            send_mail(
                "Recuperación de contraseña",
                (
                    f"Hola {usuario.nombre},\n\n"
                    f"Usa este enlace para restablecer tu contraseña:\n\n{link}\n\n"
                    "Si no fuiste tú, ignora este mensaje."
                ),
                settings.DEFAULT_FROM_EMAIL,
                [correo],
                fail_silently=False,
            )

            messages.success(request, "Se ha enviado un enlace de recuperación a tu correo.")
            return redirect("usuarios:login")

        # -------------------------
        # 3) No existe en ninguna tabla
        # -------------------------
        messages.error(request, "El correo no está registrado.")
        return redirect("usuarios:recuperar_contrasena_correo")

    return render(request, "usuarios/recuperar_contraseña_correo.html")

def reset_password(request):
    """
    Reset de contraseña para usuarios de la tabla Usuario.
    (Los admins ya usan el sistema oficial de Django)
    """
    token = request.GET.get("token")

    if not token:
        return HttpResponse("Token inválido.")

    usuario = Usuario.objects.filter(token_recuperacion=token).first()

    if not usuario:
        return HttpResponse("El enlace no es válido.")

    # Token caducado
    if usuario.fecha_token and timezone.now() > usuario.fecha_token + timedelta(hours=1):
        return HttpResponse("El enlace ha expirado.")

    if request.method == "POST":
        p1 = request.POST.get("password1")
        p2 = request.POST.get("password2")

        if p1 != p2:
            messages.error(request, "Las contraseñas no coinciden.")
            return render(request, "usuarios/password_reset_confirm.html", {"token": token})

        # Guardar la contraseña correctamente hasheada
        usuario.password = make_password(p1)
        usuario.token_recuperacion = None
        usuario.fecha_token = None
        usuario.save()

        return render(request, "usuarios/password_reset_complete.html")

    return render(request, "usuarios/password_reset_confirm.html", {"token": token})


#cambiar la clave desde el perfil del usuario 
def cambiar_contrasena_desde_perfil(request):
    """
    Vista unificada para cambiar la contraseña desde el perfil.
    Funciona para:
      - Administradores Django
      - Usuarios de la tabla Usuario (cliente, empresa, operador)
    """

    # Caso 1: usuario de Django (admin)
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        usuario_django = request.user
        usuario_custom = None

    else:
        # Caso 2: usuario de tabla Usuario
        usuario_id = request.session.get("usuario_id")

        if not usuario_id:
            messages.error(request, "Debes iniciar sesión.")
            return redirect("usuarios:login")

        usuario_custom = get_object_or_404(Usuario, id_usuario=usuario_id)
        usuario_django = None

    if request.method == "POST":

        actual = request.POST.get("password_actual")
        nueva = request.POST.get("password_nueva")
        confirmar = request.POST.get("password_confirmar")

        # ---------------------------
        # ADMIN DJANGO
        # ---------------------------
        if usuario_django:

            if not usuario_django.check_password(actual):
                messages.error(request, "La contraseña actual es incorrecta.")
                return redirect("usuarios:cambiar_contrasena_desde_perfil")

            if nueva != confirmar:
                messages.error(request, "Las contraseñas no coinciden.")
                return redirect("usuarios:cambiar_contrasena_desde_perfil")

            usuario_django.set_password(nueva)
            usuario_django.save()

            messages.success(request, "Contraseña actualizada correctamente.")
            return redirect("usuarios:login")

        # ---------------------------
        # USUARIO CUSTOM (CLIENTE, EMPRESA, OPERADOR)
        # ---------------------------
        if usuario_custom:

            if not check_password(actual, usuario_custom.password):
                messages.error(request, "La contraseña actual es incorrecta.")
                return redirect("usuarios:cambiar_contrasena_desde_perfil")

            if nueva != confirmar:
                messages.error(request, "Las contraseñas no coinciden.")
                return redirect("usuarios:cambiar_contrasena_desde_perfil")

            usuario_custom.password = make_password(nueva)
            usuario_custom.save()

            messages.success(request, "Contraseña actualizada correctamente.")
            return redirect("usuarios:login")

    # Renderizar página
    return render(request, "perfiles/cambiar_contrasena_desde_perfil.html")

# PERFIL DEL OPERADOR (vista dedicada)
def perfil_operador(request):
    usuario_id = request.session.get("usuario_id")

    if not usuario_id:
        return redirect("usuarios:login")

    operador = get_object_or_404(Usuario, id_usuario=usuario_id, rol_id=3)

    return render(request, "operadores/perfil_operador.html", {"operador": operador})
#editar informacion del cliente desde el perfil de este 



def perfil_cliente(request):
    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        messages.error(request, "Debes iniciar sesión.")
        return redirect("usuarios:login")

    try:
        cliente = Usuario.objects.get(id_usuario=usuario_id)
    except Usuario.DoesNotExist:
        messages.error(request, "Cliente no encontrado.")
        return redirect("usuarios:login")

    return render(request, "cliente/perfil_cliente.html", {
        "cliente": cliente
    })
