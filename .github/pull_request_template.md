# Pull Request

## 1. Objetivo de la iteración

<!-- Explica el problema que resuelve esta PR y el resultado observable esperado. -->

- Objetivo:
- Motivación:
- Resultado para la persona usuaria/evaluadora:

## 2. Issues y requisitos relacionados

- Closes #
- Related to #
- Enunciado (versión y sección/página):
- Requisito(s) cubierto(s):

## 3. Alcance

### Incluido

-

### Fuera de alcance

-

## 4. Cambios realizados

<!-- Agrupa por responsabilidad; evita una lista archivo por archivo sin contexto. -->

### Comportamiento

-

### Arquitectura / estructura

-

### Configuración / dependencias

-

### Documentación

-

## 5. Decisiones técnicas

- Decisión:
- Alternativas consideradas:
- Motivo de la elección:
- Trade-offs asumidos:

## 6. Definition of Done

<!-- Copia o enlaza el DoD de la issue y marca únicamente evidencia verificada. -->

- [ ] Todos los criterios de aceptación están implementados.
- [ ] Los casos nominales y de error tienen cobertura automatizada adecuada.
- [ ] No hay regresiones conocidas en el flujo completo del juego.
- [ ] `flake8` pasa con el alcance/configuración acordados.
- [ ] `mypy` pasa con los flags exigidos por el enunciado.
- [ ] El juego arranca mediante la interfaz CLI requerida.
- [ ] Los errores afectados se gestionan sin traceback.
- [ ] La documentación afectada está actualizada en inglés cuando corresponde al README.
- [ ] No se incluyen secretos, artefactos locales ni cambios ajenos a la iteración.

## 7. Pruebas y evidencias

### Comandos ejecutados

```text
# comando
# resultado exacto/resumen verificable
```

### Matriz de aceptación

| Criterio | Prueba/evidencia | Resultado |
|---|---|---|
| | | ✅ / ❌ / N/A |

### Pruebas manuales

| Escenario | Pasos | Resultado observado |
|---|---|---|
| | | |

### Evidencia visual

<!-- Capturas/GIF para cambios de UI. Indica también resolución/SO si importa. -->

- Antes:
- Después:

## 8. Impacto y compatibilidad

- Compatibilidad con Python 3.10+:
- Cambios en `config.json` o valores por defecto:
- Cambios en persistencia/highscores:
- Cambios en controles o UX:
- Cambios en empaquetado/deployment:
- Migración necesaria: Sí / No

## 9. Riesgos y mitigaciones

| Riesgo | Probabilidad/impacto | Mitigación o prueba |
|---|---|---|
| | | |

## 10. Deuda técnica y seguimiento

<!-- No ocultes trabajo pendiente; enlázalo a una issue, sin ampliar el alcance de esta PR. -->

- [ ] No queda deuda conocida dentro del alcance.
- Follow-up issues:

## 11. Checklist de revisión

### Autoría

- [ ] He revisado el diff completo contra la rama base.
- [ ] La PR contiene una sola iteración coherente y revisable.
- [ ] No hay código comentado, TODOs ambiguos ni logs temporales.
- [ ] Las nuevas dependencias están justificadas y bloqueadas en el lockfile.
- [ ] Los nombres, docstrings y type hints explican intención y contratos.
- [ ] He probado errores, límites y recursos ausentes además del happy path.

### Revisión funcional

- [ ] El comportamiento coincide con el enunciado citado.
- [ ] Los criterios de aceptación son observables y reproducibles.
- [ ] El estado (score, vidas, nivel, seed, pausa) se conserva o reinicia correctamente.
- [ ] La UI muestra la información requerida y permite completar el flujo.

### Revisión de integración

- [ ] El paquete A-Maze-ing se usa sin modificar y su fallo se maneja limpiamente.
- [ ] Los assets y rutas funcionan fuera del directorio de desarrollo.
- [ ] La configuración tolera claves desconocidas y valores inválidos según contrato.
- [ ] El highscore tolera fichero ausente/corrupto y conserva únicamente el Top 10.

## 12. Instrucciones para revisar esta PR

1.
2.
3.

## 13. Handoff

- Estado final de la iteración:
- Próxima issue recomendada:
- Bloqueos o decisiones pendientes:
