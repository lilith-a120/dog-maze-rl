import tkinter as tk
import random


# ============================================================
# 1. 기본 설정
# ============================================================

ROWS = 8
COLS = 8
CELL_SIZE = 70

# 보상
REWARD_GOAL = 100
REWARD_WALL = -10
REWARD_MOVE = 0

# Q-Learning 설정
LEARNING_RATE = 0.1       # 학습률
DISCOUNT_FACTOR = 0.9     # 할인율
EPSILON_START = 1.0       # 처음 탐험 확률
EPSILON_MIN = 0.05        # 최소 탐험 확률
EPSILON_DECAY = 0.995     # 탐험 확률 감소

MAX_STEPS = 100


# ============================================================
# 2. 미로
#
# 0 = 이동 가능
# 1 = 벽
# ============================================================

maze = [
    [0, 0, 0, 1, 0, 0, 0, 0],
    [1, 1, 0, 1, 0, 1, 1, 0],
    [0, 0, 0, 0, 0, 1, 0, 0],
    [0, 1, 1, 1, 0, 1, 0, 1],
    [0, 0, 0, 1, 0, 0, 0, 1],
    [0, 1, 0, 1, 1, 1, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 1],
    [0, 0, 0, 1, 1, 0, 0, 0]
]

# 시작 위치
START = (0, 0)

# 출구 위치
GOAL = (7, 7)


# ============================================================
# 3. 행동
#
# 0 = 위
# 1 = 아래
# 2 = 왼쪽
# 3 = 오른쪽
# ============================================================

ACTIONS = {
    0: (-1, 0),
    1: (1, 0),
    2: (0, -1),
    3: (0, 1)
}

ACTION_NAMES = {
    0: "위",
    1: "아래",
    2: "왼쪽",
    3: "오른쪽"
}


# ============================================================
# 4. Q-Table
# ============================================================
#
# Q-Table의 형태:
#
# 현재 위치 → 할 수 있는 행동 → Q값
#
# 예:
#
# Q[(0, 0)] = [0, 0, 0, 0]
#
# 순서:
# [위, 아래, 왼쪽, 오른쪽]
#
# ============================================================

q_table = {}


def create_q_table():
    """
    이동 가능한 모든 칸에 대해
    [위, 아래, 왼쪽, 오른쪽] Q값을 만든다.
    """

    global q_table

    q_table = {}

    for row in range(ROWS):
        for col in range(COLS):

            if maze[row][col] == 0:
                q_table[(row, col)] = [0.0, 0.0, 0.0, 0.0]


create_q_table()


# ============================================================
# 5. 강화학습 변수
# ============================================================

agent_pos = START

episode = 0
step_count = 0
total_reward = 0

success_count = 0

epsilon = EPSILON_START

learning = False


# ============================================================
# 6. GUI 생성
# ============================================================

window = tk.Tk()

window.title("강화학습 - 강아지 미로")

window.resizable(False, False)


# ============================================================
# 7. Canvas
# ============================================================

canvas = tk.Canvas(
    window,
    width=COLS * CELL_SIZE,
    height=ROWS * CELL_SIZE,
    bg="white"
)

canvas.pack()


# ============================================================
# 8. 정보 표시
# ============================================================

info_frame = tk.Frame(window)

info_frame.pack(pady=10)


episode_label = tk.Label(
    info_frame,
    text="Episode: 0",
    font=("Arial", 14)
)

episode_label.grid(row=0, column=0, padx=10)


reward_label = tk.Label(
    info_frame,
    text="Reward: 0",
    font=("Arial", 14)
)

reward_label.grid(row=0, column=1, padx=10)


epsilon_label = tk.Label(
    info_frame,
    text="Epsilon: 1.000",
    font=("Arial", 14)
)

epsilon_label.grid(row=0, column=2, padx=10)


success_label = tk.Label(
    info_frame,
    text="성공: 0",
    font=("Arial", 14)
)

success_label.grid(row=0, column=3, padx=10)


# ============================================================
# 9. 현재 행동 표시
# ============================================================

action_label = tk.Label(
    window,
    text="행동: -",
    font=("Arial", 14)
)

action_label.pack()


# ============================================================
# 10. 미로 그리기
# ============================================================

def draw_maze():

    canvas.delete("all")

    for row in range(ROWS):

        for col in range(COLS):

            x1 = col * CELL_SIZE
            y1 = row * CELL_SIZE

            x2 = x1 + CELL_SIZE
            y2 = y1 + CELL_SIZE

            # ------------------------------------------------
            # 벽
            # ------------------------------------------------

            if maze[row][col] == 1:

                canvas.create_rectangle(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill="black"
                )

            # ------------------------------------------------
            # 이동 가능한 칸
            # ------------------------------------------------

            else:

                canvas.create_rectangle(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill="white",
                    outline="gray"
                )

    # --------------------------------------------------------
    # 시작점
    # --------------------------------------------------------

    row, col = START

    x1 = col * CELL_SIZE
    y1 = row * CELL_SIZE

    canvas.create_rectangle(
        x1 + 5,
        y1 + 5,
        x1 + CELL_SIZE - 5,
        y1 + CELL_SIZE - 5,
        fill="lightblue",
        outline=""
    )

    canvas.create_text(
        x1 + CELL_SIZE / 2,
        y1 + CELL_SIZE / 2,
        text="START",
        font=("Arial", 10)
    )

    # --------------------------------------------------------
    # 출구
    # --------------------------------------------------------

    row, col = GOAL

    x1 = col * CELL_SIZE
    y1 = row * CELL_SIZE

    canvas.create_rectangle(
        x1 + 5,
        y1 + 5,
        x1 + CELL_SIZE - 5,
        y1 + CELL_SIZE - 5,
        fill="lightgreen",
        outline=""
    )

    canvas.create_text(
        x1 + CELL_SIZE / 2,
        y1 + CELL_SIZE / 2,
        text="EXIT",
        font=("Arial", 12, "bold")
    )


# ============================================================
# 11. 강아지 그리기
# ============================================================

def draw_dog():

    row, col = agent_pos

    center_x = col * CELL_SIZE + CELL_SIZE / 2
    center_y = row * CELL_SIZE + CELL_SIZE / 2

    # 몸
    canvas.create_oval(
        center_x - 20,
        center_y - 15,
        center_x + 20,
        center_y + 20,
        fill="gold",
        outline="black"
    )

    # 왼쪽 귀
    canvas.create_oval(
        center_x - 25,
        center_y - 25,
        center_x - 5,
        center_y - 5,
        fill="goldenrod",
        outline="black"
    )

    # 오른쪽 귀
    canvas.create_oval(
        center_x + 5,
        center_y - 25,
        center_x + 25,
        center_y - 5,
        fill="goldenrod",
        outline="black"
    )

    # 왼쪽 눈
    canvas.create_oval(
        center_x - 10,
        center_y - 5,
        center_x - 5,
        center_y,
        fill="black"
    )

    # 오른쪽 눈
    canvas.create_oval(
        center_x + 5,
        center_y - 5,
        center_x + 10,
        center_y,
        fill="black"
    )

    # 코
    canvas.create_oval(
        center_x - 4,
        center_y + 4,
        center_x + 4,
        center_y + 12,
        fill="black"
    )


# ============================================================
# 12. 화면 업데이트
# ============================================================

def draw():

    draw_maze()
    draw_dog()

    episode_label.config(
        text=f"Episode: {episode}"
    )

    reward_label.config(
        text=f"Reward: {total_reward}"
    )

    epsilon_label.config(
        text=f"Epsilon: {epsilon:.3f}"
    )

    success_label.config(
        text=f"성공: {success_count}"
    )


# ============================================================
# 13. 행동 선택
# ============================================================

def choose_action(state):

    # --------------------------------------------------------
    # Exploration
    #
    # 새로운 행동을 시도한다.
    # --------------------------------------------------------

    if random.random() < epsilon:

        return random.randint(0, 3)

    # --------------------------------------------------------
    # Exploitation
    #
    # 지금까지 배운 것 중
    # Q값이 가장 높은 행동을 선택한다.
    # --------------------------------------------------------

    q_values = q_table[state]

    max_q = max(q_values)

    # Q값이 같은 행동이 여러 개라면
    # 그중 하나를 랜덤으로 선택한다.

    best_actions = [
        action
        for action in range(4)
        if q_values[action] == max_q
    ]

    return random.choice(best_actions)


# ============================================================
# 14. 행동 실행
# ============================================================

def take_action(state, action):

    row, col = state

    dr, dc = ACTIONS[action]

    new_row = row + dr
    new_col = col + dc

    # --------------------------------------------------------
    # 미로 밖
    # --------------------------------------------------------

    if (
        new_row < 0
        or new_row >= ROWS
        or new_col < 0
        or new_col >= COLS
    ):

        return state, REWARD_WALL, False

    # --------------------------------------------------------
    # 벽
    # --------------------------------------------------------

    if maze[new_row][new_col] == 1:

        return state, REWARD_WALL, False

    new_state = (new_row, new_col)

    # --------------------------------------------------------
    # 출구
    # --------------------------------------------------------

    if new_state == GOAL:

        return new_state, REWARD_GOAL, True

    # --------------------------------------------------------
    # 일반적인 이동
    # --------------------------------------------------------

    return new_state, REWARD_MOVE, False


# ============================================================
# 15. Q값 업데이트
# ============================================================

def update_q_value(
    state,
    action,
    reward,
    next_state
):

    current_q = q_table[state][action]

    # 다음 상태에서 가장 큰 Q값
    max_next_q = max(q_table[next_state])

    # Q-Learning 공식
    new_q = current_q + LEARNING_RATE * (
        reward
        + DISCOUNT_FACTOR * max_next_q
        - current_q
    )

    q_table[state][action] = new_q


# ============================================================
# 16. 한 번의 학습 과정
# ============================================================

def learning_step():

    global agent_pos
    global episode
    global step_count
    global total_reward
    global epsilon
    global success_count

    if not learning:
        return

    # 현재 상태
    state = agent_pos

    # 행동 선택
    action = choose_action(state)

    # 행동 실행
    next_state, reward, done = take_action(
        state,
        action
    )

    # Q값 업데이트
    update_q_value(
        state,
        action,
        reward,
        next_state
    )

    # 상태 이동
    agent_pos = next_state

    # 보상 누적
    total_reward += reward

    step_count += 1

    # 화면에 행동 표시
    action_label.config(
        text=f"행동: {ACTION_NAMES[action]}   보상: {reward}"
    )

    # --------------------------------------------------------
    # 출구 도착
    # --------------------------------------------------------

    if done:

        success_count += 1

        finish_episode()

    # --------------------------------------------------------
    # 너무 오래 움직이면 강제 종료
    # --------------------------------------------------------

    elif step_count >= MAX_STEPS:

        finish_episode()

    else:

        draw()

        # 50ms 후 다음 학습
        window.after(50, learning_step)


# ============================================================
# 17. Episode 종료
# ============================================================

def finish_episode():

    global agent_pos
    global episode
    global step_count
    global total_reward
    global epsilon

    episode += 1

    # 탐험 확률 감소
    epsilon = max(
        EPSILON_MIN,
        epsilon * EPSILON_DECAY
    )

    # 시작 위치로 돌아가기
    agent_pos = START

    step_count = 0

    total_reward = 0

    draw()

    if learning:

        window.after(100, learning_step)


# ============================================================
# 18. 학습 시작
# ============================================================

def start_learning():

    global learning

    if not learning:

        learning = True

        learning_step()


# ============================================================
# 19. 학습 중지
# ============================================================

def stop_learning():

    global learning

    learning = False


# ============================================================
# 20. 학습 초기화
# ============================================================

def reset_learning():

    global agent_pos
    global episode
    global step_count
    global total_reward
    global success_count
    global epsilon
    global learning

    learning = False

    create_q_table()

    agent_pos = START

    episode = 0
    step_count = 0
    total_reward = 0
    success_count = 0

    epsilon = EPSILON_START

    action_label.config(
        text="행동: -"
    )

    draw()


# ============================================================
# 21. 버튼
# ============================================================

button_frame = tk.Frame(window)

button_frame.pack(pady=10)


start_button = tk.Button(
    button_frame,
    text="학습 시작",
    font=("Arial", 13),
    command=start_learning
)

start_button.grid(
    row=0,
    column=0,
    padx=5
)


stop_button = tk.Button(
    button_frame,
    text="학습 중지",
    font=("Arial", 13),
    command=stop_learning
)

stop_button.grid(
    row=0,
    column=1,
    padx=5
)


reset_button = tk.Button(
    button_frame,
    text="초기화",
    font=("Arial", 13),
    command=reset_learning
)

reset_button.grid(
    row=0,
    column=2,
    padx=5
)


# ============================================================
# 22. 처음 화면
# ============================================================

draw()


# ============================================================
# 23. 프로그램 실행
# ============================================================

window.mainloop()