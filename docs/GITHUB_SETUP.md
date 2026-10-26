# Настройка GitHub для команды

Это чек-лист настройки. Выполненные действия указаны отдельно; наличие этого файла не включает настройки автоматически.

## Репозиторий создан

- [shimmerycoinage/studybuddy](https://github.com/shimmerycoinage/studybuddy).
- Доступ Private, основная ветка `main`.
- Начальный README добавлен при создании, затем заменяется подготовленным описанием проекта вместе с остальными файлами.
- Публичность не менять автоматически: содержимое Public-репозитория доступно всем.

## Участники

Пользователь решил добавить двух коллег позже. Когда будут известны GitHub-логины: Settings → Collaborators → Add people. Приглашённые должны принять приглашения.

## Защита main

По задаче SB-2 нужно требовать pull request и минимум одно одобрение.

На дату проверки 26 октября 2026 года защита веток доступна в публичных репозиториях GitHub Free. Для закрытого репозитория она требует GitHub Pro, Team или Enterprise. Если выбран закрытый репозиторий на Free, описанные в CONTRIBUTING правила останутся договорённостью команды; это не равно технической защите ветки.

Источник: [документация GitHub о защите веток](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches).

После первоначальной загрузки файлов, если тариф поддерживает защиту:

1. Открыть Settings → Branches → Add branch protection rule.
2. Указать `main` в Branch name pattern.
3. Включить Require a pull request before merging.
4. Включить Require approvals и установить 1.
5. Включить Dismiss stale pull request approvals when new commits are pushed.
6. Включить Require conversation resolution before merging.
7. Включить Do not allow bypassing the above settings, если настройка доступна.
8. Оставить Allow force pushes и Allow deletions выключенными.
9. Сохранить и проверить, что правило применяется к `main`.

Назначать обязательные проверки CI нужно после появления настоящих средств проверки и их успешного запуска. Сейчас приложение и CI ещё не реализованы.

Подробности интерфейса: [создание правила защиты](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/managing-a-branch-protection-rule).

## Проверка готовности SB-2

- [ ] Репозиторий существует на GitHub, файлы загружены в `main`.
- [ ] README отображается и описывает фактическое состояние проекта.
- [ ] При создании pull request появляется шаблон.
- [ ] Оба участника приняли приглашения — когда команда будет готова их добавить.
- [ ] Защита `main` включена и требует одного одобрения, либо ограничение тарифа явно согласовано командой.
- [ ] После создания макетов в README добавлена их ссылка.

Веткам и pull request даём номер задачи `SB-…` и ссылку на неё. Автоматическую связь GitHub с Linear настраиваем отдельно; одного номера в названии недостаточно для подтверждения интеграции.
