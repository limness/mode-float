<#import "template.ftl" as layout>
<@layout.registrationLayout bodyClass="kc-login" title=msg("loginTitle",realm.displayName)>
    <div class="auth-brand">
        <div class="auth-logo">⧉</div>
        <div class="auth-title">Fly Potato</div>
        <#if realm.displayName??>
            <div class="auth-subtitle">${realm.displayName}</div>
        </#if>
    </div>

    <#if message?has_content>
        <div class="auth-alert auth-alert--${message.type}">
            ${kcSanitize(message.summary)?no_esc}
        </div>
    </#if>

    <form id="kc-form-login" class="auth-form" action="${url.loginAction}" method="post">
        <input type="hidden" name="credentialId" value="${client.clientId!}" />

        <label class="auth-field">
            <span>${msg("username")}</span>
            <input type="text" id="username" name="username" value="${login.username!}" autofocus="autofocus" autocomplete="username" />
        </label>

        <label class="auth-field">
            <span>${msg("password")}</span>
            <input type="password" id="password" name="password" autocomplete="current-password" />
        </label>

        <div class="auth-form__footer">
            <#if realm.rememberMe && login.rememberMe??>
                <label class="auth-checkbox">
                    <input type="checkbox" id="rememberMe" name="rememberMe" checked />
                    <span>${msg("rememberMe")}</span>
                </label>
            <#elseif realm.rememberMe>
                <label class="auth-checkbox">
                    <input type="checkbox" id="rememberMe" name="rememberMe" />
                    <span>${msg("rememberMe")}</span>
                </label>
            </#if>

            <#if realm.resetPasswordAllowed>
                <a class="auth-link" href="${url.loginResetCredentialsUrl}">${msg("doForgotPassword")}</a>
            </#if>
        </div>

        <button class="auth-submit" type="submit">${msg("doLogIn")}</button>
    </form>

    <#if social.providers?has_content>
        <div class="auth-divider">
            <span>${msg("identity-provider-login-label")}</span>
        </div>
        <div class="auth-social">
            <#list social.providers as provider>
                <a class="auth-social__button" href="${provider.loginUrl}">
                    <#if provider.iconClasses??>
                        <i class="${provider.iconClasses}"></i>
                    </#if>
                    <span>${provider.displayName}</span>
                </a>
            </#list>
        </div>
    </#if>

    <#if realm.registrationAllowed && !registrationDisabled??>
        <div class="auth-extra">
            ${msg("noAccount")} <a href="${url.registrationUrl}">${msg("doRegister")}</a>
        </div>
    </#if>
</@layout.registrationLayout>
