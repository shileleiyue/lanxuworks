import json
import os

class Book:
    # """图书类，封装单本图书信息"""
    def __init__(self, isbn, title, author, quantity):
        self.isbn = isbn          # 图书编号（ISBN）
        self.title = title        # 书名
        self.author = author      # 作者
        self.quantity = quantity  # 数量

    def to_dict(self):
        """将对象转换为字典，便于JSON序列化"""
        return {
            "isbn": self.isbn,
            "title": self.title,
            "author": self.author,
            "quantity": self.quantity
        }

    @classmethod
    def from_dict(cls, data):
        """从字典创建Book对象"""
        return cls(data["isbn"], data["title"], data["author"], data["quantity"])

    def __str__(self):
        return f"{self.isbn} | {self.title} | {self.author} | 数量: {self.quantity}"


class Library:
    """图书馆管理类，封装图书集合及相关操作"""
    def __init__(self, data_file="books.json"):
        self.data_file = data_file
        self.books = []          # 存储Book对象
        self.load_from_file()    # 启动时自动加载

    def load_from_file(self):
        """从JSON文件加载图书数据"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    data_list = json.load(f)
                    self.books = [Book.from_dict(item) for item in data_list]
                print(f"成功加载 {len(self.books)} 本图书信息。")
            except Exception as e:
                print(f"加载文件时出错: {e}")
        else:
            print("未找到数据文件，将创建新文件。")

    def save_to_file(self):
        """将当前图书列表保存到JSON文件"""
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump([book.to_dict() for book in self.books], f, ensure_ascii=False, indent=4)
            print("数据保存成功。")
        except Exception as e:
            print(f"保存文件时出错: {e}")

    def find_book_index(self, isbn):
        """根据ISBN查找图书在列表中的索引，若不存在返回-1"""
        for i, book in enumerate(self.books):
            if book.isbn == isbn:
                return i
        return -1

    def add_book(self, isbn, title, author, quantity):
        """添加新图书，若ISBN已存在则抛出异常"""
        if self.find_book_index(isbn) != -1:
            raise ValueError(f"图书编号 {isbn} 已存在，无法重复添加。")
        try:
            quantity = int(quantity)
            if quantity < 0:
                raise ValueError("数量不能为负数。")
        except ValueError as e:
            raise ValueError(f"数量格式错误: {e}")

        new_book = Book(isbn, title, author, quantity)
        self.books.append(new_book)
        self.save_to_file()
        print("图书添加成功。")

    def view_all_books(self):
        """显示所有图书，按添加顺序"""
        if not self.books:
            print("暂无图书信息。")
        else:
            print("\n所有图书列表:")
            print("-" * 60)
            for book in self.books:
                print(book)
            print("-" * 60)

    def query_books(self, keyword):
        """按ISBN或书名（忽略大小写，包含匹配）查询图书，返回匹配的列表"""
        keyword_lower = keyword.lower()
        result = []
        for book in self.books:
            if keyword_lower in book.isbn.lower() or keyword_lower in book.title.lower():
                result.append(book)
        return result

    def modify_quantity(self, isbn, new_quantity):
        """修改指定ISBN图书的数量"""
        idx = self.find_book_index(isbn)
        if idx == -1:
            raise ValueError(f"未找到编号为 {isbn} 的图书。")
        try:
            new_quantity = int(new_quantity)
            if new_quantity < 0:
                raise ValueError("数量不能为负数。")
        except ValueError as e:
            raise ValueError(f"数量格式错误: {e}")

        self.books[idx].quantity = new_quantity
        self.save_to_file()
        print("数量修改成功。")

    def delete_book(self, isbn):
        """删除指定ISBN的图书"""
        idx = self.find_book_index(isbn)
        if idx == -1:
            raise ValueError(f"未找到编号为 {isbn} 的图书。")
        del self.books[idx]
        self.save_to_file()
        print("图书删除成功。")

    def sort_books(self, key_type="title"):
        """按书名或作者排序并显示"""
        if not self.books:
            print("暂无图书，无法排序。")
            return
        if key_type == "title":
            sorted_books = sorted(self.books, key=lambda b: b.title)
            print("\n按书名排序显示:")
        elif key_type == "author":
            sorted_books = sorted(self.books, key=lambda b: b.author)
            print("\n按作者排序显示:")
        else:
            print("不支持的排序方式，请使用 'title' 或 'author'。")
            return

        print("-" * 60)
        for book in sorted_books:
            print(book)
        print("-" * 60)

    def batch_import(self, import_source):
        """
        批量导入图书信息。
        import_source 可以是包含多条记录的文件路径，或直接输入的文本块。
        为了简化，这里实现从文本文件导入（每行格式: ISBN,书名,作者,数量）。
        """
        if not os.path.exists(import_source):
            print(f"文件 {import_source} 不存在。")
            return
        success_count = 0
        fail_count = 0
        with open(import_source, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith("#"):  # 忽略空行和注释
                    continue
                parts = line.split(",")
                if len(parts) != 4:
                    print(f"第 {line_num} 行格式错误，跳过: {line}")
                    fail_count += 1
                    continue
                isbn, title, author, quantity_str = parts
                try:
                    self.add_book(isbn.strip(), title.strip(), author.strip(), quantity_str.strip())
                    success_count += 1
                except ValueError as e:
                    print(f"导入第 {line_num} 行失败: {e}")
                    fail_count += 1
        print(f"批量导入完成: 成功 {success_count} 条，失败 {fail_count} 条。")
        self.save_to_file()


def print_menu():
    print("\n====== 图书管理系统 ======")
    print("1. 添加图书")
    print("2. 查看所有图书")
    print("3. 查询图书 (按ISBN/书名)")
    print("4. 修改图书数量")
    print("5. 删除图书")
    print("6. 按书名排序显示")
    print("7. 按作者排序显示")
    print("8. 批量导入 (从文件)")
    print("0. 退出")


def main():
    lib = Library("books.json")

    while True:
        print_menu()
        choice = input("请选择操作: ").strip()

        if choice == "1":
            try:
                isbn = input("请输入图书编号(ISBN): ").strip()
                if not isbn:
                    raise ValueError("编号不能为空。")
                title = input("请输入书名: ").strip()
                if not title:
                    raise ValueError("书名不能为空。")
                author = input("请输入作者: ").strip()
                if not author:
                    raise ValueError("作者不能为空。")
                quantity = input("请输入数量: ").strip()
                lib.add_book(isbn, title, author, quantity)
            except ValueError as e:
                print(f"输入错误: {e}")

        elif choice == "2":
            lib.view_all_books()

        elif choice == "3":
            keyword = input("请输入ISBN或书名关键词: ").strip()
            if not keyword:
                print("关键词不能为空。")
                continue
            results = lib.query_books(keyword)
            if results:
                print("\n查询结果:")
                print("-" * 60)
                for book in results:
                    print(book)
                print("-" * 60)
            else:
                print("未找到匹配的图书。")

        elif choice == "4":
            try:
                isbn = input("请输入要修改数量的图书编号: ").strip()
                if not isbn:
                    raise ValueError("编号不能为空。")
                new_qty = input("请输入新的数量: ").strip()
                lib.modify_quantity(isbn, new_qty)
            except ValueError as e:
                print(f"操作失败: {e}")

        elif choice == "5":
            try:
                isbn = input("请输入要删除的图书编号: ").strip()
                if not isbn:
                    raise ValueError("编号不能为空。")
                lib.delete_book(isbn)
            except ValueError as e:
                print(f"操作失败: {e}")

        elif choice == "6":
            lib.sort_books("title")

        elif choice == "7":
            lib.sort_books("author")

        elif choice == "8":
            file_path = input("请输入批量导入文件路径 (每行格式: ISBN,书名,作者,数量): ").strip()
            if not file_path:
                print("文件路径不能为空。")
                continue
            lib.batch_import(file_path)

        elif choice == "0":
            print("感谢使用，再见！")
            break
        else:
            print("无效选择，请重新输入。")


if __name__ == "__main__":
    main()
