from datetime import timedelta
from django.utils import timezone
import uuid
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.hashers import make_password, check_password
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from .models import Usuario
from empresas.models import Empresa
from .forms import ClienteRegistroForm, RegistroEmpresaForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from .models import Usuario
import re
from django.core.mail import send_mail

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
# ============================================================
#  LOGIN GLOBAL PERSONALIZADO
# ============================================================


def login_global(request):

    errors = {}

    if request.method == "POST":
        
        email = request.POST.get("username").strip()
        password = request.POST.get("password")
        role = request.POST.get("role")

        # ====================================================
        # 🌟 ADMINISTRADOR (usa auth_user de Django)
        # ====================================================
        if role == "administrador":

            # 1. Buscar usuario por email
            try:
                user_obj = User.objects.get(email=email)
            except User.DoesNotExist:
                errors["email"] = "No existe un administrador con este correo."
                return render(request, "core/login.html", {"errors": errors})

            # 2. Autenticamos usando su username real
            user = authenticate(request, username=user_obj.username, password=password)

            if user is None:
                errors["password"] = "Contraseña incorrecta."
                return render(request, "core/login.html", {"errors": errors})

            # 3. Verificar permisos de admi
            if not user.is_superuser and not user.is_staff:
                errors["email"] = "Este usuario no tiene permisos de administrador."
                return render(request, "core/login.html", {"errors": errors})

            # 4. Login OK
            login(request, user)
            return redirect("administrador")

        # ====================================================
        # 🌟 OTROS ROLES -> tu tabla Usuario
        # ====================================================

        roles_dict = {
            "cliente": 1,
            "empresa": 2,
            "operador": 3,
        }

        rol_id_esperado = roles_dict.get(role)

        try:
            usuario = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            errors["email"] = "El correo no está registrado."
            return render(request, "core/login.html", {"errors": errors})

        # validar rol
        if usuario.rol_id != rol_id_esperado:
            errors["email"] = "Este usuario no pertenece al tipo seleccionado."
            return render(request, "core/login.html", {"errors": errors})

        # validar contraseña
        if not check_password(password, usuario.password):
            errors["password"] = "La contraseña es incorrecta."
            return render(request, "core/login.html", {"errors": errors})

        # guardar sesión
        request.session["usuario_id"] = usuario.id_usuario
        request.session["usuario_nombre"] = usuario.nombre
        request.session["usuario_rol"] = usuario.rol_id

        # redirecciones
        if usuario.rol_id == 1:
            return redirect("cliente")
        elif usuario.rol_id == 2:
            return redirect("empresa")
        elif usuario.rol_id == 3:
            return redirect("operador")

    return render(request, "core/login.html")
# ============================================================
#  REGISTRO CLIENTE
# ============================================================

def registro_cliente(request):
    if request.method == 'POST':
        form = ClienteRegistroForm(request.POST)
        if form.is_valid():

            if Usuario.objects.filter(email=form.cleaned_data['email']).exists():
                # añadir error al campo email y volver a mostrar el formulario
                form.add_error('email', "Este correo ya está registrado.")
                return render(request, 'core/registro_cliente.html', {'form': form})

            usuario = form.save(commit=False)
            usuario.password = make_password(form.cleaned_data['password'])
            usuario.rol_id = 1
            usuario.is_active = 1
            usuario.save()

            messages.success(request, "Registro exitoso. Ahora puedes iniciar sesión.")
            return redirect("login")
    else:
        form = ClienteRegistroForm()

    return render(request, 'core/registro_cliente.html', {'form': form})

#validaciones del perfil de cliente 
def login_view(request):
    if request.method == "POST":
        email = (request.POST.get("username") or "").strip()
        password = request.POST.get("password")
        role = request.POST.get("role")

        # VALIDACIONES BÁSICAS
        if not email or not password:
            messages.error(request, "Todos los campos son obligatorios.")
            # render (no redirect) para que el mensaje se muestre en la misma respuesta
            return render(request, "core/login.html", {"username": email, "role_selected": role})

        if "@" not in email:
            messages.error(request, "El correo no es válido.")
            return render(request, "core/login.html", {"username": email, "role_selected": role})

        # verificar si existe el usuario (en tu caso tu modelo Usuario o User de Django)
        from usuarios.models import Usuario  # o ajusta la import si tu model está en otro módulo
        try:
            usuario = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            messages.error(request, "Este correo no está registrado. Por favor regístrate.")
            return render(request, "core/login.html", {"username": email, "role_selected": role})

        # validar rol (según tu esquema)
        roles_dict = {"cliente": 1, "empresa": 2, "operador": 3, "administrador": 4}
        rol_id_esperado = roles_dict.get(role)
        if rol_id_esperado and usuario.rol_id != rol_id_esperado:
            messages.error(request, "Este usuario no pertenece al tipo seleccionado.")
            return render(request, "core/login.html", {"username": email, "role_selected": role})

        # validar contraseña (tu contraseña está hasheada con make_password)
        from django.contrib.auth.hashers import check_password
        if not check_password(password, usuario.password):
            messages.error(request, "La contraseña es incorrecta.")
            return render(request, "core/login.html", {"username": email, "role_selected": role})

        # validar estado
        if not usuario.is_active:
            messages.error(request, "Tu cuenta está desactivada. Contacta con soporte.")
            return render(request, "core/login.html", {"username": email, "role_selected": role})

        # LOGIN: guardar en sesión (tu implementación actual)
        request.session["usuario_id"] = usuario.id_usuario
        request.session["usuario_nombre"] = usuario.nombre
        request.session["usuario_rol"] = usuario.rol_id

        # redirigir según rol (ajusta nombres de url)
        if usuario.rol_id == 1:
            return redirect("cliente")
        if usuario.rol_id == 2:
            return redirect("empresa")
        if usuario.rol_id == 3:
            return redirect("operador")
        if usuario.rol_id == 4:
            return redirect("administrador")

        return redirect("inicio")

    # GET -> mostrar formulario
    return render(request, "core/login.html")

# ============================================================
#  REGISTRO EMPRESA
# ============================================================

def registro_empresa(request):
    """
    Registro de empresa:
    - crea usuario (rol empresa) inactivo
    - crea empresa con estado pendiente
    - guarda archivos en FileField
    """
    if request.method == "POST":
        print(">>> request.POST:", dict(request.POST))
        print(">>> request.FILES:", list(request.FILES.keys()))

        # datos representante
        nombre_rep = (request.POST.get("nombre_representante") or "").strip()
        email = (request.POST.get("email") or "").strip()
        telefono = (request.POST.get("telefono") or "").strip()
        password = request.POST.get("password") or ""
        password2 = request.POST.get("password2") or ""

        # datos empresa
        razon_social = (request.POST.get("razon_social") or "").strip()
        nit = (request.POST.get("nit") or "").strip()
        direccion = (request.POST.get("direccion") or "").strip()
        ciudad = (request.POST.get("ciudad") or "").strip()

        # archivos
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
            print(">>> errores:", errores)
            return render(request, "core/registro_empresa.html")

        try:
            with transaction.atomic():
                # usuario
                usuario = Usuario.objects.create(
                    nombre=nombre_rep,
                    email=email,
                    telefono=telefono,
                    password=make_password(password),
                    rol_id=2,
                    is_active=False
                )

                # empresa
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

                print(">>> Usuario creado:", usuario.id_usuario)
                print(">>> Empresa creada:", empresa.id_empresa)

            messages.success(request, "Registro completado. Empresa pendiente de validación.")
            return redirect("login")

        except Exception as exc:
            print(">>> ERROR registro_empresa:", exc)
            messages.error(request, "Error interno al registrar la empresa")
            return render(request, "core/registro_empresa.html")

    return render(request, "core/registro_empresa.html")


# ============================================================
#  REGISTRO OPERADOR
# ============================================================

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
            rol_id=3,  # Operador
            is_active=1
        )

        messages.success(request, "Operador registrado correctamente.")
        return redirect('login')

    return render(request, 'core/registro_operador.html')



# ============================================================
#  LOGOUT
# ============================================================

def logout_view(request):
    request.session.flush()  # limpia toda la sesión
    return redirect("login")

def validar_email(request):
    email = request.GET.get("email")
    existe = Usuario.objects.filter(email=email).exists()
    return JsonResponse({"existe": existe})


def cliente_view(request):
    return render(request, "core/cliente.html")


#operador cambiar contraseña atra vez del correo 


from .models import Usuario  # ajusta si tu import es distinto

# PERFIL DEL OPERADOR
def perfil_operador(request):
    usuario_id = request.session.get("usuario_id")

    if not usuario_id:
        return redirect("usuarios:login")

    operador = get_object_or_404(Usuario, id_usuario=usuario_id, rol_id=3)

    return render(request, "operadores/perfil_operador.html", {"operador": operador})


# ENVIAR CORREO DE CAMBIO DE CONTRASEÑA
def operador_enviar_cambio_contrasena(request):
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        return redirect("usuarios:login")

    usuario = get_object_or_404(Usuario, id_usuario=usuario_id, rol_id=3)

    # generar token único
    token = str(uuid.uuid4())
    usuario.token_recuperacion = token
    usuario.fecha_token = timezone.now()
    usuario.save()

    # crear link absoluto
    link = request.build_absolute_uri(f"/accounts/reset-password/?token={token}")

    # enviar correo
    send_mail(
        "Cambio de contraseña",
        f"Hola {usuario.nombre},\n\n"
        f"Puedes restablecer tu contraseña usando este enlace:\n\n{link}\n\n"
        "Si no solicitaste esto, ignora este mensaje.",
        settings.DEFAULT_FROM_EMAIL,
        [usuario.email],
        fail_silently=False,
    )

    messages.success(request, "El enlace de cambio de contraseña fue enviado a tu correo.")
    return redirect("usuarios:perfil_operador")


# CAMBIO DE CONTRASEÑA (TOKEN)
def reset_password(request):
    token = request.GET.get("token")
    if not token:
        return HttpResponse("Token no proporcionado.", status=400)

    usuario = Usuario.objects.filter(token_recuperacion=token).first()
    if not usuario:
        return HttpResponse("El enlace es inválido o ya fue usado.", status=400)

    # verificar expiración (30 minutos)
    if usuario.fecha_token is None or usuario.fecha_token < timezone.now() - timedelta(minutes=30):
        return HttpResponse("El enlace de recuperación ha expirado.", status=400)

    if request.method == "POST":
        nueva = request.POST.get("password")
        repetir = request.POST.get("password2")

        if not nueva or not repetir:
            messages.error(request, "Todos los campos son obligatorios.")
            return render(request, "operadores/operador_cambiar_password.html", {"token": token})

        if nueva != repetir:
            messages.error(request, "Las contraseñas no coinciden.")
            return render(request, "operadores/operador_cambiar_password.html", {"token": token})

        # guardar contraseña hasheada
        Usuario.objects.filter(id_usuario=usuario.id_usuario).update(
            password=make_password(nueva),
            token_recuperacion=None,
            fecha_token=None
        )

        messages.success(request, "La contraseña fue cambiada exitosamente. Inicia sesión con la nueva contraseña.")
        return redirect("usuarios:login")

    return render(request, "operadores/operador_cambiar_password.html", {"token": token})
