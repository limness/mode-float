# Fly Potato Keycloak Login Theme

Custom Keycloak login theme that mirrors the Fly Potato branding. The goal is to let users authenticate through Keycloak while keeping the same look-and-feel as the in-app React login screen.

## Structure

```
keycloak-theme/
└── fly-potato-login/
    └── login/
        ├── theme.properties
        ├── template.ftl
        ├── login.ftl
        └── resources/
            └── css/
                └── theme.css
```

- `theme.properties` – registers the theme and points to the custom CSS.
- `template.ftl` – wraps Keycloak screens into a simplified layout.
- `login.ftl` – the actual login page: username/password form, remember me, forgot password, social providers.
- `theme.css` – styling that matches the Fly Potato mockups.

## Enabling the Theme

1. Copy the folder `fly-potato-login` into `/opt/keycloak/themes/` of your Keycloak instance.
2. Restart Keycloak (or the container) so the theme becomes available.
3. In the Keycloak admin console open **Realm Settings → Themes** and set **Login Theme** to `fly-potato-login`.
4. Visit your login URL (for example `/realms/<realm>/protocol/openid-connect/auth?...`) and verify the custom layout renders.

### Docker Example

```bash
docker cp keycloak-theme/fly-potato-login <keycloak_container>:/opt/keycloak/themes/
docker restart <keycloak_container>
```

## Notes

- Social providers (e.g. Google) automatically appear inside the “войти через” block when configured in Keycloak.
- Forgot password and registration links are shown only if they are enabled for the realm.
- All server-side error messages are displayed at the top of the card.

Feel free to adjust colors or layout in `resources/css/theme.css` to better match updated branding.
