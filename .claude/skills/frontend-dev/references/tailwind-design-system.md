# Tailwind CSS 디자인 시스템

## 색상 팔레트

### 주요 색상
```javascript
// Primary (파란색 - 신뢰, 전문성)
bg-blue-50    // 매우 밝은 배경
bg-blue-100   // 밝은 배경
bg-blue-500   // 기본
bg-blue-600   // 버튼, 링크
bg-blue-700   // hover 상태
bg-blue-900   // 텍스트

// Success (녹색 - 성공, 완료)
bg-green-50   // 배경
bg-green-500  // 아이콘, 배지
bg-green-600  // 버튼

// Warning (노란색 - 주의, 대기)
bg-yellow-50  // 배경
bg-yellow-500 // 아이콘, 배지

// Error (빨간색 - 오류, 경고)
bg-red-50     // 배경
bg-red-500    // 텍스트, 아이콘
bg-red-600    // 버튼

// Neutral (회색 - 배경, 텍스트)
bg-gray-50    // 페이지 배경
bg-gray-100   // 카드 배경
bg-gray-300   // 테두리
bg-gray-500   // 보조 텍스트
bg-gray-900   // 주요 텍스트
```

## 타이포그래피

### 텍스트 크기
```css
text-xs     // 12px - 캡션, 라벨
text-sm     // 14px - 보조 텍스트
text-base   // 16px - 본문
text-lg     // 18px - 리드 텍스트
text-xl     // 20px - 소제목
text-2xl    // 24px - 제목
text-3xl    // 30px - 대제목
text-4xl    // 36px - 히어로
```

### 폰트 굵기
```css
font-normal    // 400 - 본문
font-medium    // 500 - 강조
font-semibold  // 600 - 제목
font-bold      // 700 - 주요 제목
```

## 간격 (Spacing)

### Padding/Margin
```css
p-2   // 8px
p-4   // 16px
p-6   // 24px
p-8   // 32px

m-2   // 8px
m-4   // 16px
m-6   // 24px
m-8   // 32px
```

### 간격 규칙
- 컴포넌트 내부: `p-4` ~ `p-6`
- 컴포넌트 간: `space-y-4` ~ `space-y-6`
- 섹션 간: `space-y-8` ~ `space-y-12`
- 페이지 패딩: `px-6 py-8`

## 버튼 스타일

### Primary 버튼
```jsx
<button className="px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
  Primary Button
</button>
```

### Secondary 버튼
```jsx
<button className="px-6 py-3 bg-gray-200 text-gray-800 font-semibold rounded-lg hover:bg-gray-300 transition-colors">
  Secondary Button
</button>
```

### Outline 버튼
```jsx
<button className="px-6 py-3 border-2 border-blue-600 text-blue-600 font-semibold rounded-lg hover:bg-blue-50 transition-colors">
  Outline Button
</button>
```

### Danger 버튼
```jsx
<button className="px-6 py-3 bg-red-600 text-white font-semibold rounded-lg hover:bg-red-700 transition-colors">
  Danger Button
</button>
```

## 입력 필드 (Input)

### 기본 입력
```jsx
<input
  type="text"
  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
  placeholder="입력하세요"
/>
```

### 에러 상태
```jsx
<input
  type="text"
  className="w-full px-4 py-2 border-2 border-red-500 rounded-lg focus:ring-2 focus:ring-red-500 outline-none"
/>
<p className="mt-1 text-sm text-red-600">에러 메시지</p>
```

### 비활성화 상태
```jsx
<input
  type="text"
  disabled
  className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-100 text-gray-500 cursor-not-allowed"
/>
```

## 카드 (Card)

### 기본 카드
```jsx
<div className="bg-white rounded-lg shadow p-6">
  <h3 className="text-lg font-semibold mb-4">카드 제목</h3>
  <p className="text-gray-600">카드 내용</p>
</div>
```

### Hover 카드
```jsx
<div className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-6 cursor-pointer">
  <h3 className="text-lg font-semibold mb-2">클릭 가능한 카드</h3>
</div>
```

## 배지 (Badge)

```jsx
// Success
<span className="px-3 py-1 bg-green-100 text-green-800 text-sm font-medium rounded-full">
  완료
</span>

// Warning
<span className="px-3 py-1 bg-yellow-100 text-yellow-800 text-sm font-medium rounded-full">
  대기
</span>

// Error
<span className="px-3 py-1 bg-red-100 text-red-800 text-sm font-medium rounded-full">
  실패
</span>

// Info
<span className="px-3 py-1 bg-blue-100 text-blue-800 text-sm font-medium rounded-full">
  진행중
</span>
```

## 모달 (Modal)

```jsx
<div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
  <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">모달 제목</h2>
      <p className="text-gray-600 mb-6">모달 내용</p>
      <div className="flex justify-end space-x-3">
        <button className="px-4 py-2 bg-gray-200 rounded-lg hover:bg-gray-300">
          취소
        </button>
        <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
          확인
        </button>
      </div>
    </div>
  </div>
</div>
```

## 폼 레이아웃

### 수직 폼
```jsx
<form className="space-y-4">
  <div>
    <label className="block text-sm font-medium text-gray-700 mb-2">
      이름
    </label>
    <input
      type="text"
      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
    />
  </div>

  <div>
    <label className="block text-sm font-medium text-gray-700 mb-2">
      이메일
    </label>
    <input
      type="email"
      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
    />
  </div>
</form>
```

### 수평 폼
```jsx
<form className="space-y-4">
  <div className="grid grid-cols-3 gap-4 items-center">
    <label className="text-sm font-medium text-gray-700">
      이름
    </label>
    <input
      type="text"
      className="col-span-2 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
    />
  </div>
</form>
```

## 테이블

```jsx
<div className="overflow-x-auto">
  <table className="min-w-full divide-y divide-gray-200">
    <thead className="bg-gray-50">
      <tr>
        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
          이름
        </th>
        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
          상태
        </th>
        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
          작업
        </th>
      </tr>
    </thead>
    <tbody className="bg-white divide-y divide-gray-200">
      <tr className="hover:bg-gray-50">
        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
          홍길동
        </td>
        <td className="px-6 py-4 whitespace-nowrap">
          <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
            활성
          </span>
        </td>
        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
          <button className="text-blue-600 hover:text-blue-900">편집</button>
        </td>
      </tr>
    </tbody>
  </table>
</div>
```

## 반응형 디자인

### Breakpoints
```css
sm:  // 640px+  (모바일 가로)
md:  // 768px+  (태블릿)
lg:  // 1024px+ (데스크탑)
xl:  // 1280px+ (대형 데스크탑)
2xl: // 1536px+ (초대형)
```

### 반응형 그리드
```jsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  {/* 모바일: 1열, 태블릿: 2열, 데스크탑: 3열 */}
</div>
```

### 반응형 패딩
```jsx
<div className="px-4 md:px-6 lg:px-8">
  {/* 모바일: 16px, 태블릿: 24px, 데스크탑: 32px */}
</div>
```

## 애니메이션

### Transition
```css
transition-colors  // 색상 전환
transition-opacity // 투명도 전환
transition-all     // 모든 속성 전환
duration-200       // 200ms
duration-300       // 300ms
ease-in-out        // 가감속
```

### Hover 효과
```jsx
<button className="bg-blue-600 hover:bg-blue-700 transform hover:scale-105 transition-all">
  Hover me
</button>
```

### Fade In
```jsx
<div className="opacity-0 animate-fade-in">
  Fading in...
</div>

/* tailwind.config.js */
module.exports = {
  theme: {
    extend: {
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
      },
    },
  },
}
```

## 접근성 (Accessibility)

### Focus 스타일
```jsx
<button className="focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2">
  Accessible Button
</button>
```

### Screen Reader 전용
```jsx
<span className="sr-only">화면 리더에서만 읽힘</span>
```

## 다크 모드 (선택사항)

```jsx
<div className="bg-white dark:bg-gray-900 text-gray-900 dark:text-white">
  다크 모드 지원
</div>
```
