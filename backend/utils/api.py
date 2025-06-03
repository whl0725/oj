import functools
from django.http import HttpResponse
def validate_serializer(serializer):
    """
    @validate_serializer(TestSerializer)
    def post(self, request):
        return self.success(request.data)
    """
    # 定义一个内部函数validate，用于装饰视图方法
    def validate(view_method):
        # 使用functools.wraps保持被装饰函数的元信息
        @functools.wraps(view_method)
        def handle(*args, **kwargs):
            # args[0]通常是指向实例本身的引用，args[1,json]是请求对象
            self = args[0]
            request = args[1]
            # 使用传入的serializer类创建一个序列化器实例，并传入请求数据
            s = serializer(data=request.data)
            # 检查序列化器数据是否有效
            if s.is_valid():
                # 如果有效，创建一个新的字典来存储序列化后的数据
                validated_data = s.validated_data
                # 将序列化器实例附加到请求对象上，以便后续使用
                request.serializer = s
                # 调用原始的视图方法，并将序列化后的数据作为参数传递
                #return view_method(*args, **kwargs)
                return view_method(*args, validated=validated_data, **kwargs)
            else:
                # 如果无效，调用实例的invalid_serializer方法处理无效的序列化器
                return HttpResponse("序列化错误" ,status=520)

        # 返回handle函数，作为装饰后的视图方法
        return handle

    # 返回validate函数，用于装饰视图方法
    return validate


