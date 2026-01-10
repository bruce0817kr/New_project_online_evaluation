// Template: 새 컴포넌트 생성 시 사용
// 파일명: [ComponentName].jsx

import React from 'react';
import PropTypes from 'prop-types';

/**
 * [컴포넌트 설명]
 *
 * @component
 * @param {Object} props - 컴포넌트 props
 * @param {string} props.title - 제목
 * @param {function} props.onClick - 클릭 핸들러
 * @param {boolean} [props.disabled=false] - 비활성화 여부
 *
 * @example
 * <ExampleComponent
 *   title="제목"
 *   onClick={handleClick}
 *   disabled={false}
 * />
 */
export const ExampleComponent = ({
  title,
  onClick,
  disabled = false,
  className = '',
}) => {
  // 내부 상태
  const [internalState, setInternalState] = React.useState(null);

  // 이펙트
  React.useEffect(() => {
    // 초기화 로직
    return () => {
      // 정리 로직
    };
  }, []);

  // 이벤트 핸들러
  const handleClick = () => {
    if (disabled) return;
    onClick?.();
  };

  return (
    <div className={`example-component ${className}`}>
      <h3 className="text-lg font-semibold">{title}</h3>
      <button
        onClick={handleClick}
        disabled={disabled}
        className="mt-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
      >
        클릭
      </button>
    </div>
  );
};

// PropTypes 정의
ExampleComponent.propTypes = {
  title: PropTypes.string.isRequired,
  onClick: PropTypes.func,
  disabled: PropTypes.bool,
  className: PropTypes.string,
};

// Default Props
ExampleComponent.defaultProps = {
  disabled: false,
  className: '',
};

export default ExampleComponent;
