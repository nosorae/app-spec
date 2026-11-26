# 플랫폼 공식 근거

[앱 기획 쓰는 법 v0.1](../SPEC.md) 의 낱말 가운데 개발에 바로 걸리는 것이 Android 와 iOS 공식 문서의 어느 문장에서 나왔는지 모았다. 메모리 상태의 유지 여부, 저장소 종류, 화면 이동, 백그라운드 작업, 알림이 대상이다. 두 플랫폼에서 뜻이 통하는 낱말만 형식에 넣었고, 다르게 동작하는 곳은 [두 플랫폼이 다르게 동작하는 곳](#두-플랫폼이-다르게-동작하는-곳) 에 적었다.

앱 기획 쓰는 법은 앱의 화면, 값, 동작을 기획자와 개발자가 한 파일에 YAML 로 적는 형식이다. 명세를 쓰는 사람이 낱말의 뜻을 플랫폼 동작과 맞춰 보거나, 개발자가 명세의 낱말을 어떤 API 로 만들지 찾을 때 이 노트를 쓴다. 이 노트에 나오는 형식의 낱말은 다음과 같다.

- `상태` 와 `소스`: 화면에 보이거나 판단에 쓰는 값과, 그 값이 있는 곳. 소스는 네트워크, 디스크, 메모리, 기기, 계산 가운데 하나다
- `구성 변경에도 유지`, `프로세스 종료에도 유지`: 소스가 메모리인 상태에 예, 아니오로 적는 두 질문
- `시작 화면`, `흐름`, `링크`: 앱을 켰을 때 맨 아래에 놓이는 화면, 값을 같이 쓰는 화면 묶음, 화면으로 바로 들어오는 주소
- `이동`, `기기`: 동작의 단계. `이동` 은 다른 화면으로 가고, `기기` 는 권한 요청처럼 기기의 기능을 쓴다. `이동` 의 방식 가운데 `비우고 이동` 은 열려 있던 화면을 닫고 시작 화면 위에 새 화면만 남긴다
- `백그라운드 작업`: 화면이 닫혀 있어도 도는 일. `미뤄도 됨`(시스템이 실행을 늦춰도 되는지), `조건`, `다시 시도`, `겹치면`, `진행 알림` 을 적는다. `겹치면` 은 같은 작업이 이미 있을 때 어떻게 하는지이고, `건너뜀` 은 새것을 버리고, `바꿈` 은 있던 것을 취소하고 새것을 걸고, `줄 세움` 은 있던 것이 끝난 뒤 새것을 한다
- `알림`: `분류`(사용자가 종류별로 켜고 끄는 묶음), `중요도`, `앱을 보고 있을 때`(앱을 보는 중에 알림이 오면 어떻게 하는지)를 적는다

조사일은 2026-11-11 이다. Flutter, React Native, 웹은 조사하지 않았다.

## 낱말 대응표

| 형식의 낱말 | Android | iOS |
|---|---|---|
| `구성 변경에도 유지: 예` | ViewModel | 화면 회전 때 화면이나 상태를 다시 만든다는 문장을 찾지 못했다 |
| `프로세스 종료에도 유지: 예` | Saved state (`rememberSaveable`, `SavedStateHandle`) | 상태 복원 (`SceneStorage`, UIKit 의 state preservation) |
| 디스크 종류 `설정` | Preferences | UserDefaults |
| 디스크 종류 `디비` | Room | SwiftData |
| 디스크 종류 `보안 저장소` | 조사하지 않았다 | Keychain |
| 디스크 종류 `파일` | 앱 전용 파일 | 파일 시스템. Caches 와 tmp 는 시스템이 지울 수 있다 |
| `시작 화면` | start destination | 조사하지 않았다 |
| `흐름` | 중첩 내비게이션 그래프 | 조사하지 않았다 |
| `링크` | 딥링크 | Universal link |
| 백그라운드 작업 `미뤄도 됨: 예` | WorkManager | BGTaskScheduler |
| 백그라운드 작업 `미뤄도 됨: 아니오` | 정확한 알람, 포그라운드 서비스 | 실행 시각을 보장하는 작업 API 는 찾지 못했다. 정한 시각에 알림을 띄우는 것은 로컬 알림 트리거가 한다 |
| 백그라운드 작업 `조건` | Constraints | `requiresNetworkConnectivity`, `requiresExternalPower` |
| 백그라운드 작업 `다시 시도` | 백오프 정책 | 찾지 못했다 |
| 백그라운드 작업 `겹치면` | 고유 작업의 충돌 정책 KEEP, REPLACE, APPEND | 찾지 못했다 |
| 백그라운드 작업 `진행 알림` | 포그라운드 서비스의 알림 | 조사하지 않았다 |
| 알림 `분류` | 알림 채널 | 대응하는 개념을 찾지 못했다 |
| 알림 `중요도` | 채널의 중요도 | 중단 수준(interruption level) |
| 알림 `앱을 보고 있을 때` | 원문 표를 받지 못했다 | `willPresent` 델리게이트 |

표에 나온 이름은 다음과 같다.

- ViewModel, Saved state: Android 에서 화면의 값을 들고 있는 두 방법. Saved state 는 `rememberSaveable` 이나 `SavedStateHandle` 에 맡겨 둔 값을 시스템이 보관했다가 되살려 준다
- SceneStorage: iOS 에서 창(씬)마다 작은 값을 맡겨 두면 시스템이 되살려 주는 기능. UIKit 의 state preservation 도 같은 일을 한다
- Preferences 와 UserDefaults: 이름과 값을 짝지어 저장하는 작은 저장소. 앞이 Android, 뒤가 iOS
- Room 과 SwiftData: 데이터베이스. 앞이 Android, 뒤가 iOS
- Keychain: iOS 에서 암호화해서 저장하는 곳
- 앱 전용 파일: Android 에서 그 앱만 읽고 쓰는 파일 위치. iOS 의 Caches 와 tmp 는 다시 만들 수 있는 파일을 두는 폴더다
- 딥링크와 Universal link: 링크로 앱의 특정 화면을 여는 기능. 앞이 Android, 뒤가 iOS
- WorkManager 와 BGTaskScheduler: 백그라운드 작업을 예약하는 API. 앞이 Android, 뒤가 iOS. `requiresNetworkConnectivity` 와 `requiresExternalPower` 는 BGTaskScheduler 로 긴 작업을 걸 때 붙이는 옵션이다
- 정확한 알람, 포그라운드 서비스: Android 에서 정한 시각에 일을 시키는 기능, 화면을 꺼도 계속 도는 일을 알림과 함께 돌리는 기능
- 중단 수준: iOS 에서 알림이 사용자를 얼마나 방해해도 되는지를 정하는 단계
- `willPresent` 델리게이트: iOS 에서 앱을 보고 있을 때 알림이 오면 불리는 메서드

## 메모리 상태의 유지 여부

Android 의 UI 상태 저장 문서([Save UI states](https://developer.android.com/topic/libraries/architecture/saving-states?hl=en))에 세 가지 방법을 견준 표가 있다. 형식의 두 질문은 이 표의 둘째 줄과 셋째 줄이다.

| | ViewModel | Saved state | Persistent storage |
|---|---|---|---|
| Storage location | in memory | in memory | on disk or network |
| Survives configuration change | Yes | Yes | Yes |
| Survives system-initiated process death | No | Yes | Yes |
| Survives user complete screen dismissal/finish() | No | No | Yes |

> A user expects a screen's UI state to remain the same throughout a configuration change, such as rotation or switching into multi-window mode.
>
> However, the system may destroy the application process while the user is away interacting with other apps.

풀이. 사용자는 화면을 돌려도 화면 상태가 그대로이기를 바란다. 그리고 사용자가 다른 앱을 쓰는 사이 시스템이 앱 프로세스를 종료할 수 있다. 형식의 `구성 변경에도 유지` 와 `프로세스 종료에도 유지` 가 이 두 상황을 묻는다. 표의 넷째 줄(사용자가 화면을 완전히 닫음) 뒤에도 남아야 하는 값은 맨 오른쪽 칸뿐이고, 형식에서는 소스를 디스크나 네트워크로 적는다.

> Usually, data stored in saved state is transient state that depends on user input or navigation.

같은 표의 Data limitations 줄은 Saved state 칸에 "only for primitive types and simple, small objects such as String" 이라고 적는다.

풀이. 프로세스 종료 뒤에 되살리는 값은 입력이나 화면 이동에 딸린 작은 값이어야 한다. 형식이 `프로세스 종료에도 유지: 예` 를 입력하던 글자, 고른 탭 같은 작은 값에만 쓰라고 한 이유다.

구성 변경이 무엇인지는 [Handle configuration changes](https://developer.android.com/guide/topics/resources/runtime-changes?hl=en) 가 나열한다.

> Some device configurations can change while the app is running.

이 문장 뒤에 App display size, Screen density (display scaling), Screen orientation, Font size and weight, Locale, Dark theme versus light theme, Keyboard availability 가 나열된다.

> The system recreates an Activity when a configuration change occurs.

풀이. 구성 변경은 회전만이 아니다. 화면 크기, 글자 크기, 언어, 다크 모드도 들어가고, 이때 시스템이 화면(Activity)을 다시 만든다. 형식의 풀이 "화면 회전, 다크 모드 전환, 글자 크기나 언어 변경, 창 크기 변경" 이 이 목록에서 나왔다.

iOS 쪽 문장은 다음과 같다.

> The foreground has priority over memory and other system resources, and the system terminates background apps as needed to make those resources available.

([Preparing your UI to run in the background](https://developer.apple.com/documentation/uikit/preparing-your-ui-to-run-in-the-background))

> State preservation isn't a substitute for saving your app's data to disk.

([Preserving your app's UI across launches](https://developer.apple.com/documentation/uikit/preserving-your-app-s-ui-across-launches))

> If the Scene is explicitly destroyed (e.g. the switcher snapshot is destroyed on iPadOS or the window is closed on macOS), the data is also destroyed.
>
> Ensure that the data you use with SceneStorage is lightweight.

([SceneStorage](https://developer.apple.com/documentation/swiftui/scenestorage))

> Don't use state properties for persistent storage because the life cycle of state variables mirrors the view life cycle.

([Managing user interface state](https://developer.apple.com/documentation/swiftui/managing-user-interface-state))

풀이. iOS 도 시스템이 백그라운드 앱을 종료한다. 그때 되살릴 값을 두는 곳(SceneStorage)은 가벼운 값만 넣게 돼 있고, 사용자가 창을 직접 닫으면 지워진다. 화면 상태 복원이 디스크 저장을 대신하지 못한다는 것도 Android 표와 같다. 그래서 `프로세스 종료에도 유지` 는 두 플랫폼에서 같은 뜻으로 쓸 수 있다.

화면 회전에 대해서는 iOS 문서에서 이 문장만 찾았다.

> ... be prepared to handle size class changes while your app runs, because factors like device orientation can change at runtime.

([horizontalSizeClass](https://developer.apple.com/documentation/swiftui/environmentvalues/horizontalsizeclass))

풀이. iOS 문서는 회전을 화면 크기 분류가 바뀌는 일로 설명한다. 회전 때 화면이나 상태를 다시 만든다는 문장은 찾지 못했다. `구성 변경에도 유지` 가 iOS 에서 따로 할 일이 있는 질문인지는 확인하지 못했다.

## 적힌 위치가 범위라는 규칙

[State holders and UI state](https://developer.android.com/topic/architecture/ui-layer/stateholders?hl=en)

> Screen UI state is what you need to display on the screen.
>
> UI element state refers to properties intrinsic to UI elements that influence how they are rendered.

풀이. Android 문서는 화면이 보여 줄 내용인 상태와 UI 요소 하나에 딸린 상태를 나눈다. 형식에서 화면에 적는 상태와 컴포넌트에 적는 상태가 이 구분이다.

[Data layer](https://developer.android.com/topic/architecture/data-layer?hl=en)

> UI-oriented operations are only relevant when the user is on a specific screen, and they're canceled when the user moves away from that screen.
>
> Business-oriented operations cannot be canceled. They should survive process death.

풀이. 화면에 딸린 일은 사용자가 화면을 떠나면 취소되고, 꼭 끝내야 하는 일은 프로세스가 종료돼도 이어져야 한다. 형식의 규칙 "화면이 닫히거나 앱이 종료돼도 끝까지 해야 하는 일은 백그라운드 작업으로 적는다" 가 여기서 나왔다.

## 소스

[Data layer](https://developer.android.com/topic/architecture/data-layer?hl=en)

> Each data source class should have the responsibility of working with only one source of data, which can be a file, a network source, or a local database.
>
> The source of truth can be a data source—for example, the database—or even an in-memory cache that the repository might contain.

[Build an offline-first app](https://developer.android.com/topic/architecture/data-layer/offline-first?hl=en)

> The local data source is the canonical source of truth for the app.
>
> When writing data in offline-first apps, there are three strategies to consider.

풀이. 값이 있는 곳을 파일, 네트워크, 로컬 데이터베이스, 메모리 캐시로 나누는 것은 Android 데이터 레이어 문서의 구분과 같다. 연결이 없어도 쓰는 앱은 기기 저장소를 기준으로 삼으라고 한다. 형식에서 네트워크 상태의 `보관`(받은 값을 기기 어디에 두는지)에 디스크 저장소를 적거나, 형식의 달리기 기록 앱 예시처럼 소스를 디스크로 적고 백그라운드 작업으로 서버에 올리는 것이 이 구성이다. 연결이 없을 때 쓰기를 어떻게 할지는 세 가지가 있다고 하니, 연결이 없을 때 한 일을 어떻게 할지를 명세에 적어야 한다.

저장소 종류는 [Data and file storage overview](https://developer.android.com/training/data-storage?hl=en) 의 구분을 따랐다.

> Store private, primitive data in key-value pairs.
>
> Store structured data in a private database using the Room persistence library.

풀이. 첫 문장이 Preferences, 둘째가 Databases 설명이다. 형식의 `설정` 과 `디비` 다.

iOS 쪽은 다음과 같다.

> The defaults system stores information on disk in an unencrypted format.

([UserDefaults](https://developer.apple.com/documentation/foundation/userdefaults))

> ... store small bits of user data in an encrypted database called a keychain.

([Keychain services](https://developer.apple.com/documentation/security/keychain-services))

> Purgeable data is app data that the system can delete without affecting the app's execution and that the app can re-create if it needs.

([Optimizing your app's data for iCloud backup](https://developer.apple.com/documentation/foundation/optimizing-your-app-s-data-for-icloud-backup))

풀이. UserDefaults 는 암호화하지 않고 디스크에 둔다. 토큰 같은 값은 Keychain 에 둔다. 형식이 `설정` 과 `보안 저장소` 를 다른 종류로 둔 이유다. 종류가 `파일` 인 저장소는 시스템이 지워도 되는 파일인지를 `설명` 에 적어야 한다.

## 화면 이동

[Principles of navigation](https://developer.android.com/guide/navigation/principles?hl=en)

> Every app you build has a fixed start destination.
>
> These conditional screens should not be considered start destinations because users see these screens only in certain cases.
>
> The back stack always has the start destination of the app at the bottom of the stack.
>
> When deep linking to a destination within your app's task, any existing back stack for your app's task is removed and replaced with the deep-linked back stack.

풀이. 앱에는 고정된 시작 화면이 하나 있고, 로그인처럼 조건에 따라 보이는 화면은 시작 화면이 아니며, 시작 화면은 쌓인 화면의 맨 아래에 있다. 링크로 들어오면 쌓여 있던 화면을 새 것으로 바꾼다. 형식의 `시작 화면` 풀이, `비우고 이동` 의 뜻(시작 화면 위에 새 화면만 남긴다), `링크` 로 들어왔을 때의 기본 동작이 이 네 문장을 따른다.

[Nested graphs](https://developer.android.com/guide/navigation/design/nested-graphs?hl=en)

> Login flows, wizards, or other subflows within your app are usually best represented as nested navigation graphs.

풀이. 형식의 `흐름` 이 이것이다.

iOS 쪽은 다음과 같다.

> When users tap or click a universal link, the system redirects the link directly to your app without routing through the person's default web browser or your website.

([Allowing apps and websites to link to your content](https://developer.apple.com/documentation/xcode/allowing-apps-and-websites-to-link-to-your-content))

> Use a path to support deep links, state restoration, or other kinds of programmatic navigation.

([NavigationStack](https://developer.apple.com/documentation/swiftui/navigationstack))

풀이. iOS 는 링크로 들어왔을 때 화면을 어떻게 쌓을지를 플랫폼이 정해 주지 않고, 앱이 쌓인 화면 목록(path)을 직접 만든다.

## 백그라운드 작업

[Background tasks overview](https://developer.android.com/develop/background-work/background-tasks?hl=en) 는 어떤 API 를 쓸지 고르는 질문을 절 제목으로 둔다.

> Does the task need to continue running while the app is in the background?
>
> Will there be a bad user experience if the task is deferred or interrupted?

풀이. 둘째 질문이 형식의 `미뤄도 됨` 이다.

[Define work requests](https://developer.android.com/develop/background-work/background-tasks/persistent/getting-started/define-work?hl=en)

> When multiple constraints are specified, your work will run only when all the constraints are met.
>
> In the event that a constraint becomes unmet while your work is running, WorkManager will stop your worker. The work will then be retried when all the constraints are met.
>
> WorkManager supports 2 backoff policies, LINEAR and EXPONENTIAL.
>
> The minimum repeat interval that can be defined is 15 minutes (same as the JobScheduler API).

풀이. 조건은 전부 맞아야 하고, 도는 중에 안 맞게 되면 멈췄다가 다시 맞으면 다시 한다. 형식의 `조건` 풀이가 이 두 문장이다. `다시 시도` 에 적는 간격은 일정하게 늘리거나 두 배씩 늘리는 두 가지가 있다. 되풀이하는 작업의 `언제` 를 15분보다 짧게 적으면 WorkManager 로는 만들 수 없다.

[Managing work](https://developer.android.com/develop/background-work/background-tasks/persistent/how-to/manage-work?hl=en)

> Unique work is a powerful concept that guarantees that you only have one instance of work with a particular name at a time.
>
> KEEP existing work and ignore the new work.
>
> REPLACE existing work with the new work.
>
> APPEND the new work to the end of the existing work.

풀이. 형식의 `겹치면` 값 `건너뜀`, `바꿈`, `줄 세움` 이 차례로 KEEP, REPLACE, APPEND 다. 같은 작업인지를 이름으로 가르는 것도 여기서 왔다.

[Schedule alarms](https://developer.android.com/develop/background-work/services/alarms?hl=en)

> If your app's core functionality depends on a precisely-timed alarm—such as for an alarm clock app or a calendar app—then it's OK to use an exact alarm instead.
>
> It's highly recommended that you create an inexact alarm whenever possible.

[Foreground services overview](https://developer.android.com/develop/background-work/services/fgs?hl=en)

> Foreground services show a status bar notification, to make users aware that your app is performing a task in the foreground and is consuming system resources.

풀이. 정확한 시각이 꼭 필요한 앱만 정확한 알람을 쓰고, 될 수 있으면 정확하지 않은 알람을 쓰라고 한다. `미뤄도 됨: 아니오` 는 꼭 필요한 작업에만 적어야 한다. 화면을 꺼도 계속되는 일은 사용자가 알 수 있게 알림을 띄워야 하고, 형식의 `진행 알림` 이 그것이다.

iOS 쪽은 다음과 같다.

> BGAppRefreshTask is for short-duration tasks that expect quick results, such as downloading a stock quote.

([Using background tasks to update your app](https://developer.apple.com/documentation/uikit/using-background-tasks-to-update-your-app))

> The system decides the best time to launch your background task, and provides your app up to 30 seconds of background runtime.

([Choosing background strategies for your app](https://developer.apple.com/documentation/backgroundtasks/choosing-background-strategies-for-your-app))

> Processing tasks run only when the device is idle.

([BGProcessingTask](https://developer.apple.com/documentation/backgroundtasks/bgprocessingtask))

> However, the system doesn't guarantee launching the task at the specified date, but only that it won't begin sooner.

([earliestBeginDate](https://developer.apple.com/documentation/backgroundtasks/bgtaskrequest/earliestbegindate))

풀이. iOS 의 예약 작업은 실행 시각을 시스템이 정한다. 짧은 갱신 작업은 30초까지, 긴 처리 작업은 기기가 쉬고 있을 때만 돈다. 적어 준 날짜는 그보다 일찍 돌지 않는다는 뜻일 뿐이다. 형식의 `미뤄도 됨: 예` 에 해당하고, `아니오` 에 해당하는 작업 API 는 찾지 못했다.

> If the user terminates the app from the multitasking screen, the system cancels all of the session's background transfers.

([background(withIdentifier:)](https://developer.apple.com/documentation/foundation/urlsessionconfiguration/background(withidentifier:)))

> The system treats background notifications as low priority: you can use them to refresh your app's content, but the system doesn't guarantee their delivery.

([Pushing background updates to your app](https://developer.apple.com/documentation/usernotifications/pushing-background-updates-to-your-app))

풀이. 사용자가 앱을 직접 종료하면 백그라운드 전송이 취소된다. 화면에 보이지 않는 푸시로 앱을 깨우는 방법은 전달이 보장되지 않는다. 형식이 서버 푸시로 시작하는 작업에는 못 받았을 때 값을 맞추는 방법을 적으라고 한 이유다.

## 알림

[Create and manage notification channels](https://developer.android.com/develop/ui/views/notifications/channels?hl=en)

> Starting in Android 8.0 (API level 26), all notifications must be assigned to a channel.
>
> After you create a notification channel, you can't change the notification behaviors.

풀이. Android 의 알림은 모두 채널에 속하고, 채널을 만든 뒤에는 앱이 동작을 바꿀 수 없다. 형식의 `분류` 가 채널이다. 한 번 내보내면 못 바꾸니 처음에 정해야 한다.

같은 문서의 중요도 표는 가장 높은 단계를 "Makes a sound and appears as a heads-up notification.", 그다음을 "Makes a sound.", 그다음을 "Makes no sound." 로 설명한다. 형식의 `높음`, `보통`, `낮음` 이 이 셋이다.

[Notification runtime permission](https://developer.android.com/develop/ui/views/notifications/notification-permission?hl=en) 은 Android 13 이상에 새로 설치한 앱은 "notifications are off by default" 라고 적는다.

iOS 쪽은 다음과 같다.

> The first time your app makes this authorization request, the system prompts the person to grant or deny the request and records that response.
>
> Subsequent authorization requests don't prompt the person.

([Asking permission to use notifications](https://developer.apple.com/documentation/usernotifications/asking-permission-to-use-notifications))

풀이. 두 플랫폼 모두 알림을 보내려면 사용자의 허락이 필요하고, iOS 는 시스템 창이 처음 한 번만 뜬다. 명세에 알림 권한을 언제 묻는지 적어야 한다. 형식에서는 동작의 `기기` 단계에 알림 권한을 요청한다고 적는다.

> The system adds the notification to the notification list without lighting up the screen or playing a sound.

([UNNotificationInterruptionLevel.passive](https://developer.apple.com/documentation/usernotifications/unnotificationinterruptionlevel/passive))

풀이. iOS 의 가장 낮은 중단 수준 설명이다. 형식의 `중요도: 낮음` 과 같은 뜻이다.

> If your delegate does not implement this method, the system behaves as if you had passed the UNNotificationPresentationOptionNone option to the completionHandler block.

([userNotificationCenter(_:willPresent:withCompletionHandler:)](https://developer.apple.com/documentation/usernotifications/unusernotificationcenterdelegate/usernotificationcenter(_:willpresent:withcompletionhandler:)))

풀이. 앱을 보고 있는 중에 온 알림은 앱이 받아서 어떻게 보일지 정한다. 이 메서드를 만들지 않으면 아무것도 표시되지 않는다. 형식이 `앱을 보고 있을 때` 를 꼭 적게 한 이유다.

> Specify the conditions for delivering your notification using a UNCalendarNotificationTrigger, UNTimeIntervalNotificationTrigger, or UNLocationNotificationTrigger object.

([Scheduling a notification locally from your app](https://developer.apple.com/documentation/usernotifications/scheduling-a-notification-locally-from-your-app))

풀이. iOS 는 정한 날짜와 시각, 일정 시간 뒤, 어떤 장소에 들어가거나 나올 때 알림을 띄우도록 시스템에 맡길 수 있다.

## 두 플랫폼이 다르게 동작하는 곳

명세를 쓸 때 아래 여섯 가지는 플랫폼마다 다르게 될 수 있다는 것을 알고 적는다.

1. 정한 시각에 하는 일. Android 는 정확한 알람으로 할 수 있고 권한이 걸린다. iOS 의 예약 작업은 실행 시각을 보장하지 않는다. 정한 시각에 필요한 것이 알림이면 두 플랫폼 모두 되지만, 알림 말고 다른 일이면 iOS 에서 안 될 수 있다
2. 사용자가 앱을 직접 종료한 뒤. iOS 는 백그라운드 전송을 취소한다. Android 에서 어떻게 되는지는 조사하지 않았다
3. 알림 분류. Android 는 채널 단위로 사용자가 기기 설정에서 켜고 끈다. iOS 에서 여기에 대응하는 개념은 찾지 못했다. 종류별로 켜고 끄게 하려면 iOS 에서는 앱 안에 설정 화면을 만들어야 할 수 있다
4. 구성 변경. Android 는 화면을 다시 만든다. iOS 에서 같은 일이 있는지는 문장을 찾지 못했다
5. 알림 권한. Android 13 이상은 새로 설치하면 알림이 꺼져 있고 언제 물을지는 앱이 정한다. iOS 는 시스템 창이 처음 한 번만 뜬다
6. 링크나 알림으로 들어왔을 때 쌓이는 화면. Android 내비게이션 원칙은 쌓여 있던 화면을 바꾼다고 정해 두었다. iOS 는 앱이 정한다. 형식은 `링크` 의 기본 동작을 Android 원칙에 맞췄다

## 확인하지 못한 것

- FCM 의 메시지 종류(notification, data)와 앱 상태별 처리. 예전 문서 주소가 없어졌고, 지금 문서의 표를 원문 그대로 받지 못했다. 그래서 `보내는 곳: 서버` 인 알림이 Android 에서 앱을 보고 있을 때 어떻게 처리되는지는 인용하지 못했다
- iOS 에서 화면 회전 때 상태가 다시 만들어지는지
- iOS 에서 사용자가 앱을 강제 종료했을 때 상태 복원이 어떻게 되는지. 샘플 앱을 디버깅할 때의 동작을 설명한 문장만 찾았다
- iOS 에 알림 채널에 대응하는 개념이 있는지. 열어 본 문서에 없었다는 뜻이고, 없다는 것을 확인한 것은 아니다
- Android 의 보안 저장소, 포그라운드 서비스 종류별 규칙, 사용자가 앱을 강제 종료한 뒤의 WorkManager 동작

## 참고 자료

인용문은 원문 페이지에 그 문장이 있는지 스크립트로 확인했다(2026-11-11). Apple 문서는 같은 문서의 JSON 주소로 받아서 확인했다. 기존 형식 조사는 [2026-11-11-기존-형식-벤치마크](benchmark.md) 에 있다.

- Android, Save UI states: https://developer.android.com/topic/libraries/architecture/saving-states?hl=en
- Android, Handle configuration changes: https://developer.android.com/guide/topics/resources/runtime-changes?hl=en
- Android, State holders and UI state: https://developer.android.com/topic/architecture/ui-layer/stateholders?hl=en
- Android, Data layer: https://developer.android.com/topic/architecture/data-layer?hl=en
- Android, Build an offline-first app: https://developer.android.com/topic/architecture/data-layer/offline-first?hl=en
- Android, Data and file storage overview: https://developer.android.com/training/data-storage?hl=en
- Android, Principles of navigation: https://developer.android.com/guide/navigation/principles?hl=en
- Android, Background tasks overview: https://developer.android.com/develop/background-work/background-tasks?hl=en
- Android, Define work requests: https://developer.android.com/develop/background-work/background-tasks/persistent/getting-started/define-work?hl=en
- Android, Managing work: https://developer.android.com/develop/background-work/background-tasks/persistent/how-to/manage-work?hl=en
- Android, Schedule alarms: https://developer.android.com/develop/background-work/services/alarms?hl=en
- Android, Notification channels: https://developer.android.com/develop/ui/views/notifications/channels?hl=en
- Apple, SceneStorage: https://developer.apple.com/documentation/swiftui/scenestorage
- Apple, Choosing background strategies for your app: https://developer.apple.com/documentation/backgroundtasks/choosing-background-strategies-for-your-app
- Apple, Pushing background updates to your app: https://developer.apple.com/documentation/usernotifications/pushing-background-updates-to-your-app
- Apple, Asking permission to use notifications: https://developer.apple.com/documentation/usernotifications/asking-permission-to-use-notifications
